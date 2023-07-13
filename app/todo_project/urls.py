from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('todo_api.urls'), name='task'),
    path('api/user/', include('user_api.urls'), name='user'),
    path("api/rest/auth/", include("dj_rest_auth.urls"), name='rest-auth'),  # endpoints provided by dj-rest-auth
    path('api/auth/', include('auth_api.urls'), name='auth'),
]
