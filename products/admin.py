from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','product_price','product_stock','category','seller']
    search_fields = ['product_name']
    list_filter = ['category','seller']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']
    search_fields = ['category_name']

admin.site.register(Category , CategoryAdmin)
admin.site.register(Product , ProductAdmin)
