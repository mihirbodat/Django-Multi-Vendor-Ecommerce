from django.db import models
from django.contrib.auth.models import User

class SellerProfile(models.Model):
    seller_user = models.OneToOneField(User , on_delete=models.CASCADE)
    shop_name = models.CharField('shop_name',max_length=200)
    shop_description = models.TextField('shop_description',blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.shop_name

