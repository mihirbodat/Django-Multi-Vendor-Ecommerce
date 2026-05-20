from django.urls import path
from users import views

urlpatterns = [
    path('', views.home , name='home'),
    path('registeruser', views.registeruser , name='registeruser'),
    path('loginuser', views.loginuser , name='loginuser'),
    path('logoutuser' , views.logoutuser , name='logoutuser'),
    path('seller_dashboard' , views.seller_dashboard , name='seller_dashboard'),
    path('buyer_search_product' , views.buyer_search_product , name='buyer_search_product'),
]
