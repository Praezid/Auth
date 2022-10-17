from authentication import views
from django.urls import path

urlpatterns = [
    path('users', views.RegisterApiView.as_view(), name='register'),
    path('login', views.LoginApiView.as_view(), name='login'),
    path('users/<int:id>', views.UserRetrieveUpdateAPIView.as_view(), name='users'),
    path('users/<int:id>/notifications', views.UserNotificationListAPIView.as_view(), name='user-notifications'),
]
