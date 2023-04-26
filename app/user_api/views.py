"""
Core views
"""
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .serializers import UserSerializer, AuthSerializer

User = get_user_model()


class UserConnectionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return Response({
            "detail": "Connection successfully!"
        })


class UserTokenView(ObtainAuthToken):
    serializer_class = AuthSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user