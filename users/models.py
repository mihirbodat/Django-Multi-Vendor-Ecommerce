from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os 

class SellerProfile(models.Model):
    seller_user = models.OneToOneField(User , on_delete=models.CASCADE)
    shop_name = models.CharField('shop_name',max_length=200)
    shop_description = models.TextField('shop_description',blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.shop_name

class Review(models.Model):
    buyer = models.ForeignKey(User , on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product' , on_delete=models.CASCADE)
    order_item = models.ForeignKey('orders.OrderItem' , on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')])
    message = models.CharField('Message' , max_length=1000)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.buyer.username} - {self.product} - {self.rating}⭐"
    
class ReviewImage(models.Model):
    review = models.ForeignKey(Review , on_delete=models.CASCADE , related_name='images')
    image = models.ImageField(upload_to='reviews/' , blank=True , null= True)

    def __str__(self):
        return f"{self.review.buyer.username} - {self.review.product}"
    

@receiver(post_delete , sender=ReviewImage)
def delete_review_image(sender , instance , **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)