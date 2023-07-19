"""
URLs mapping for users.
"""
from django.urls import path
from .views import UserMeView

app_name = 'user_api'
urlpatterns = [
    path('me/', UserMeView.as_view(), name='me')
]
