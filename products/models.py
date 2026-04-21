from django.db import models
from users.models import SellerProfile

class Category(models.Model):
    category_name = models.CharField(max_length=200)
    category_description = models.TextField(blank=True)

    def __str__(self):
        return self.category_name
    

class Product(models.Model):
    seller = models.ForeignKey(SellerProfile , on_delete=models.CASCADE)
    category = models.ForeignKey(Category , on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_description = models.TextField(blank=True)
    product_price = models.DecimalField(max_digits=10 , decimal_places=2)
    product_stock = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to='products/' , blank=True)
    create_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product_name
    