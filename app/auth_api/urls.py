from django.urls import path, include
from .views import GoogleLoginView, ConnectionView

urlpatterns = [
    path("social/login/google/", GoogleLoginView.as_view(), name="google"),
    path("verify/", ConnectionView.as_view(), name="connection-verify"),
]