from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('todo_api.urls', namespace='task')),
    path('api/auth/', include('user_api.urls', namespace='user')),
]
