from django.urls import path
from .views import GoogleLoginView, ConnectionView

app_name = "auth_api"
urlpatterns = [
    path("social/login/google/", GoogleLoginView.as_view(), name="google"),
    path("verify/", ConnectionView.as_view(), name="connection-verify"),
]
