from rest_framework import serializers


class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    scene = serializers.ChoiceField(choices=["register", "login"])


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(min_length=6)


class LoginPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField()


class LoginCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

