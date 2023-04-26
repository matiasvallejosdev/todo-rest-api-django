"""
URLs mapping for users.
"""
from django.urls import path
from .views import UserCreateView, UserTokenView, UserConnectionView, UserMeView  # UserRetrieveView

app_name = 'user_api'
urlpatterns = [
    # path('<int:pk>/', UserRetrieveView.as_view(), 'user'),
    path('connection/', UserConnectionView.as_view(), name='connection'),
    path('create/', UserCreateView.as_view(), name='create'),
    path('token/', UserTokenView.as_view(), name='token'),
    path('me/', UserMeView.as_view(), name='me')
]
