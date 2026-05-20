from django.urls import path
from products import views

urlpatterns = [
    path('add_product',views.add_product, name='add_product'),
    path('seller_products',views.seller_products, name='seller_products'),
    path('edit_product/<int:id>/' , views.edit_product , name='edit_product'),
    path('update_product/<int:id>/' , views.update_product , name='update_product'),
    path('seller_search_product' , views.seller_search_product , name='seller_search_product'),
    path('delete_product/<int:id>/' , views.delete_product , name='delete_product'),
    path('product_detail/<int:id>/',views.product_detail, name='product_detail'),
]
