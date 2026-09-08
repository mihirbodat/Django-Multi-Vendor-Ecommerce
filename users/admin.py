from django.contrib import admin
from .models import *
from django.contrib.auth.models import User

class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['seller_user' , 'shop_name' , 'is_approved']
    list_editable = ['is_approved']
    search_fields = ['shop_name' , 'seller_user__username']

admin.site.register(SellerProfile , SellerProfileAdmin)
admin.site.register(Review)
admin.site.register(ReviewImage)
admin.site.register(Wishlist)
