from django.contrib import admin
from .models import *

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user','total_price','created_at']
    search_fields = ['user__username']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order','product','seller','quantity','status','cancelled_by']
    list_filter = ['status' , 'cancelled_by']
    search_fields = ['product__product_name']

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order , OrderAdmin)
admin.site.register(OrderItem , OrderItemAdmin)
