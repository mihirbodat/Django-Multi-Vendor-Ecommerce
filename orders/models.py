from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from users.models import SellerProfile

class Cart(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart , on_delete=models.CASCADE)
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"
    
class Order(models.Model):
    STATUS_CHOICES = [('Pending','Pending'),
                      ('Confirmed' , 'Confirmed'),
                      ('Shipped' , 'Shipped'),
                      ('Delivered' , 'Delivered'),
                      ('Cancelled' , 'Cancelled'),]
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10 , decimal_places=2 , default=0)
    status = models.CharField(max_length=20 , choices=STATUS_CHOICES , default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order , on_delete=models.CASCADE)
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    seller = models.ForeignKey(SellerProfile , on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10 , decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"

