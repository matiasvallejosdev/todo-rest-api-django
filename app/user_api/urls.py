"""
URLs mapping for users.
"""
from django.urls import path
from .views import UserMeView, UserCreateView

app_name = 'user_api'
urlpatterns = [
    path('me/', UserMeView.as_view(), name='me'),
    path('create/', UserCreateView.as_view(), name='create')
]
