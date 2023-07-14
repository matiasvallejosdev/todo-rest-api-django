from rest_framework.views import APIView
from rest_framework import permissions

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from rest_framework.response import Response


class GoogleLoginView(SocialLoginView):  # Authorization Code grant
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/api/auth/callback/google"
    client_class = OAuth2Client


class ConnectionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        return Response({
            "detail": "Connection successfully!"
        })
