from django.urls import path
from products import views

urlpatterns = [
    path('add_product',views.add_product, name='add_product'),
    path('seller_product_list',views.seller_product_list, name='seller_product_list'),
    path('edit_product/<int:id>' , views.edit_product , name='edit_product'),
    path('update_product/<int:id>' , views.update_product , name='update_product'),
    path('search_product' , views.search_product , name='search_product'),
    path('delete_product/<int:id>' , views.delete_product , name='delete_product'),
    path('buyer_product_list',views.buyer_product_list, name='buyer_product_list'),
]
