from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from config.response import ok, error
from .services.vod import VodService
from .services.cos import CosService

class UnifiedModelViewSet(ModelViewSet):
    """
    Unified ViewSet that wraps responses in the standard format.
    Handles pagination if present.
    """
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        # Handle paginated response
        if isinstance(response.data, dict) and 'results' in response.data and 'count' in response.data:
            data = response.data['results']
            # Attempt to extract pagination info
            page = int(request.query_params.get('page', 1))
            # Try to get page_size from paginator or query param
            page_size = 20
            if hasattr(self, 'paginator') and self.paginator:
                page_size = self.paginator.page_size
            
            # Override with query param if present and valid
            try:
                ps = int(request.query_params.get('page_size'))
                if ps > 0:
                    page_size = ps
            except (TypeError, ValueError):
                pass

            meta = {
                'pagination': {
                    'total': response.data['count'],
                    'page': page,
                    'page_size': page_size
                }
            }
            return ok(data=data, meta=meta)
        
        return ok(data=response.data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return ok(data=response.data, status=201)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return ok(data=response.data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return ok(data=response.data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        # Return 200 OK with standard success format instead of 204 No Content
        # This ensures frontend interceptors can handle it consistently
        return ok(message="deleted")


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return error("VALIDATION_ERROR", "No file provided", status=400)
        
        # Get upload type from query params
        upload_type = request.query_params.get('type', 'image')
        
        # Map type to path prefix
        prefix_map = {
            'avatar': 'avatars',
            'course_cover': 'courses/covers',
            'category_cover': 'categories/covers',
            'material': 'materials',
            'document': 'documents',
            'image': 'images',
            'file': 'files'
        }
        
        path_prefix = prefix_map.get(upload_type, 'uploads')
        
        try:
            service = CosService()
            url = service.upload_file(file_obj, path_prefix=path_prefix)
            return ok({"url": url})
        except Exception as e:
            return error("SERVER_ERROR", str(e), status=500)


class VodSignatureView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get VOD signatures.
        Query Params:
        - type: 'upload' (default) or 'play'
        - file_id: required if type is 'play'
        """
        try:
            sig_type = request.query_params.get('type', 'upload')
            service = VodService()

            if sig_type == 'upload':
                # Only admin can upload (adjust as needed)
                if not request.user.is_staff and not request.user.is_superuser:
                     return error("PERMISSION_DENIED", "Only admins can upload videos", status=403)
                     
                signature = service.get_upload_signature()
                return ok({"signature": signature})
            
            elif sig_type == 'play':
                file_id = request.query_params.get('file_id')
                if not file_id:
                    return error("VALIDATION_ERROR", "file_id is required for play signature", status=422)
                
                # TODO: Add logic to check if user has access to this video
                
                result = service.get_play_signature(file_id)
                return ok(result)
            
            else:
                return error("VALIDATION_ERROR", f"Invalid signature type: {sig_type}", status=400)

        except Exception as e:
            return error("SERVER_ERROR", str(e), status=500)
