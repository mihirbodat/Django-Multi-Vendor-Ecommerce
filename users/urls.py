from django.urls import path
from users import views

urlpatterns = [
    path('', views.home , name='home'),
    path('registeruser', views.registeruser , name='registeruser'),
    path('loginuser', views.loginuser , name='loginuser'),
    path('logoutuser' , views.logoutuser , name='logoutuser'),
]
