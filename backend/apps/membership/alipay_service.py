from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.domain.AlipayTradeRefundModel import AlipayTradeRefundModel
from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import logging
import traceback
import json
from rest_framework.exceptions import ValidationError, APIException
from apps.membership.models import MemberOrder
from apps.membership.services import process_payment_success, check_and_expire_order

logger = logging.getLogger(__name__)

class AlipayService:
    """支付宝服务"""

    @staticmethod
    def _validate_payment_params(order):
        """
        验证支付参数的有效性

        Args:
            order: 订单对象

        Raises:
            ValidationError: 参数验证失败
        """
        # 验证订单号
        if not order.order_no or len(str(order.order_no)) > 64:
            raise ValidationError('订单号格式不正确或过长')

        # 验证金额
        if order.amount <= 0:
            raise ValidationError('支付金额必须大于0')

        if order.amount > Decimal('999999.99'):
            raise ValidationError('支付金额超出限制')

        # 验证商品名称 (使用 plan_name)
        product_name = getattr(order, 'plan_name', '会员订单')
        if not product_name or len(str(product_name)) > 256:
            raise ValidationError('商品名称不正确或过长')

        logger.debug(f"订单参数验证通过: {order.order_no}, 金额: {order.amount}")

    @staticmethod
    def _get_alipay_client():
        """
        获取支付宝客户端

        Returns:
            DefaultAlipayClient: 支付宝客户端对象

        Raises:
            APIException: 支付宝配置不完整或SDK未安装
        """

        # 检查支付宝配置
        alipay_config = getattr(settings, 'ALIPAY_CONFIG', {})

        if not alipay_config:
            raise APIException('支付宝配置不存在，请在settings.py中配置ALIPAY_CONFIG')

        required_keys = ['app_id', 'app_private_key', 'alipay_public_key', 'server_url']
        for key in required_keys:
            if key not in alipay_config or not alipay_config[key]:
                # 允许 return_url 和 notify_url 为空
                pass
            elif not alipay_config[key]:
                 # 检查必要字段是否为空字符串
                 raise APIException(f'支付宝配置缺少必要字段或为空: {key}')

        try:
            # 创建支付宝客户端配置
            client_config = AlipayClientConfig()
            client_config.server_url = alipay_config['server_url']
            client_config.app_id = alipay_config['app_id']
            client_config.app_private_key = alipay_config['app_private_key']
            client_config.alipay_public_key = alipay_config['alipay_public_key']

            # 创建客户端
            client = DefaultAlipayClient(alipay_client_config=client_config, logger=logger)

            return client
        except Exception as e:
            raise APIException(f'创建支付宝客户端失败: {str(e)}')

    @staticmethod
    def create_payment_request(order):
        """
        创建支付宝支付请求

        Args:
            order: 订单对象

        Returns:
            dict: 支付请求信息，包含支付URL或HTML表单

        Raises:
            APIException: 支付宝服务调用失败
            ValidationError: 参数验证失败
        """
        try:
            # ✅ 验证支付参数
            AlipayService._validate_payment_params(order)

            # 获取支付宝客户端
            client = AlipayService._get_alipay_client()

            # 构建支付模型（业务参数）
            model = AlipayTradePagePayModel()
            model.out_trade_no = str(order.order_no)  # 订单号（确保是字符串）
            model.total_amount = str(order.amount)  # 支付金额（转换为字符串）
            model.subject = str(order.plan_name)  # 商品标题（确保是字符串）
            model.body = f"会员开通订单: {order.order_no}"  # 商品描述
            model.product_code = "FAST_INSTANT_TRADE_PAY"  # 产品码

            # 创建支付请求
            request = AlipayTradePagePayRequest(biz_model=model)

            # 设置公共参数：支付成功后的返回URL（同步通知）
            return_url = settings.ALIPAY_CONFIG.get('return_url')
            if return_url:
                request.return_url = return_url
            
            # 设置异步通知URL
            notify_url = settings.ALIPAY_CONFIG.get('notify_url')
            if notify_url:
                request.notify_url = notify_url

            # 执行请求，获取支付URL或HTML表单
            # http_method="GET" 返回支付URL
            # http_method="POST" 返回HTML表单
            response = client.page_execute(request, http_method="GET")

            logger.info(f"支付宝支付请求已创建: {order.order_no}")

            # 返回支付信息
            return {
                'payment_url': response,
                'order_no': order.order_no,
                'amount': str(order.amount),
                'platform': 'alipay'
            }
        except (ValidationError, APIException):
            raise
        except Exception as e:
            logger.error(f"创建支付宝支付请求失败: {str(e)}\n{traceback.format_exc()}")
            raise APIException(f"支付宝服务调用失败: {str(e)}")

    @staticmethod
    def _parse_alipay_response(response_content):
        """
        安全解析支付宝响应

        Args:
            response_content: 支付宝返回的响应内容

        Returns:
            dict: 解析后的业务数据

        Raises:
            APIException: 响应格式错误或包含错误信息
        """
        try:
            # 如果是字符串则解析，如果是字典则直接使用
            if isinstance(response_content, str):
                 response_dict = json.loads(response_content)
            else:
                 response_dict = response_content
        except json.JSONDecodeError as e:
            logger.error(f"支付宝响应JSON解析失败: {str(e)}")
            raise APIException(f"支付宝响应格式错误: {str(e)}")

        # 检查是否有业务响应数据
        if 'alipay_trade_query_response' in response_dict:
            biz_response = response_dict['alipay_trade_query_response']
        elif 'alipay_trade_refund_response' in response_dict:
            biz_response = response_dict['alipay_trade_refund_response']
        else:
            biz_response = response_dict

        # 检查是否有错误响应
        if biz_response.get('code') != '10000':
            error_msg = biz_response.get('sub_msg', biz_response.get('msg', '未知错误'))
            logger.error(f"支付宝返回错误: code={biz_response.get('code')}, msg={error_msg}")
            raise APIException(f"支付宝错误: {error_msg}")

        return biz_response

    @staticmethod
    def refund_order(order):
        """
        申请退款

        Args:
            order: 订单对象

        Returns:
            dict: 退款结果

        Raises:
            APIException: 退款失败
        """
        try:
            # 验证
            if order.status != "PAID":
                raise ValidationError("订单未支付，无法退款")
            
            client = AlipayService._get_alipay_client()

            # 构建退款请求
            model = AlipayTradeRefundModel()
            model.out_trade_no = str(order.order_no)
            model.refund_amount = str(order.amount)
            model.refund_reason = "用户/管理员申请退款"

            request = AlipayTradeRefundRequest(biz_model=model)

            # 执行请求
            response_content = client.execute(request)
            
            response = AlipayService._parse_alipay_response(response_content)

            # 检查 fund_change (本次退款是否发生了资金变化)
            if response.get("fund_change") == "Y":
                 logger.info(f"订单 {order.order_no} 退款成功")
            
            return {
                "order_no": order.order_no,
                "refund_fee": response.get("refund_fee"),
                "gmt_refund_pay": response.get("gmt_refund_pay"),
                "fund_change": response.get("fund_change")
            }

        except (ValidationError, APIException):
            raise
        except Exception as e:
            logger.error(f"支付宝退款失败: {str(e)}\n{traceback.format_exc()}")
            raise APIException(f"退款失败: {str(e)}")
    @staticmethod
    def query_payment_status(order_no):
        """
        查询支付宝支付结果并同步本地状态
            order_no: 订单号

        Returns:
            dict: 支付结果信息
        """
        try:
            # 获取订单
            try:
                order = MemberOrder.objects.get(order_no=order_no)
            except MemberOrder.DoesNotExist:
                raise ValidationError("订单不存在")

            client = AlipayService._get_alipay_client()

            # 构建查询请求
            model = AlipayTradeQueryModel()
            model.out_trade_no = str(order_no)

            request = AlipayTradeQueryRequest(biz_model=model)

            # 执行请求
            # execute 返回的是字典（如果 client 配置正确）还是字符串？
            # DefaultAlipayClient.execute returns the response content string usually, unless configured otherwise.
            # Actually alipay-sdk-python `execute` returns the response body string.
            response_content = client.execute(request)
            
            response = AlipayService._parse_alipay_response(response_content)

            trade_status = response.get("trade_status")

            # 支付成功
            if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
                # 验证支付金额是否一致 (防止恶意篡改金额)
                total_amount = response.get("total_amount")
                if total_amount and Decimal(total_amount) != order.amount:
                    logger.critical(f"支付金额不一致! 订单: {order.order_no}, 订单金额: {order.amount}, 支付宝金额: {total_amount}")
                    # 不抛出异常，而是返回错误状态，避免前端误以为支付成功
                    # 或者抛出异常阻断流程
                    raise ValidationError(f"支付金额不一致: 订单{order.amount} vs 实付{total_amount}")

                # 只有未支付（或意外已过期但实际已支付）的订单才处理
                # 允许 EXPIRED 状态是因为可能存在用户打开支付页面后超过30分钟才支付的情况，此时支付宝已扣款，我们应尽量履约
                if order.status in ["PENDING", "EXPIRED"]:
                     # 传递完整响应给 process_payment_success 以记录交易流水
                     process_payment_success(order, "ALIPAY", external_data=response)
            else:
                # 如果未支付成功，检查本地订单是否应该过期
                check_and_expire_order(order)
            
            return {
                "order_no": order_no,
                "trade_status": trade_status,
                "total_amount": response.get("total_amount"),
                "trade_no": response.get("trade_no"),
                "send_pay_date": response.get("send_pay_date"),
                "buyer_user_id": response.get("buyer_user_id")
            }

        except (ValidationError, APIException):
            raise
        except Exception as e:
            logger.error(f"查询支付宝订单状态失败: {str(e)}\n{traceback.format_exc()}")
            raise APIException(f"查询失败: {str(e)}")
