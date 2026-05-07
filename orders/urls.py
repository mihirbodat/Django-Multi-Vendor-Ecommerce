from django.urls import path
from orders import views

urlpatterns = [
    path('add_to_cart/<int:id>/',views.add_to_cart , name='add_to_cart'),
    path('cart',views.cart , name='cart'),
    path('update_quantity/<int:id>/<str:action>/' , views.update_quantity , name='update_quantity'),
    path('remove_item/<int:id>/',views.remove_item , name='remove_item'),
    path('checkout',views.checkout, name='checkout'),
    path('buy_now/<int:id>/',views.buy_now, name='buy_now'),
    path('place_order',views.place_order, name='place_order'),
    path('order_confirmation/<int:id>/',views.order_confirmation, name='order_confirmation'),
    path('orders',views.orders,name='orders'),
]
