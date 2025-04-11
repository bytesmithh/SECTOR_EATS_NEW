from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    role = models.CharField(max_length=100,default="customer")

    


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    cuisine_type = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)
    description = models.TextField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    delivery_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



class MenuItem(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"
