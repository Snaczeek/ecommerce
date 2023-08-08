import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

# Create your models here.
class Product(models.Model):
    name = models.TextField(max_length=50)
    description = models.TextField(max_length=4000)
    price = models.DecimalField(default=1.00, validators=[MinValueValidator(0.0)], decimal_places=2, max_digits=10)
    image = models.ImageField(upload_to='images/')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

@receiver(pre_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    # Get the path to the image file
    if instance.image:
        image_path = instance.image.path

        # Check if the file exists and delete it
        if os.path.exists(image_path):
            os.remove(image_path)

@receiver(pre_save, sender=Product)
def update_product_image(sender, instance, **kwargs):
    # Check if the instance is being updated
    if instance.pk:
        try:
            # Get the original instance from the database
            original_instance = Product.objects.get(pk=instance.pk)

            # Check if the image field is being updated
            if original_instance.image and original_instance.image != instance.image:
                # Get the path to the original image file
                image_path = original_instance.image.path

                # Check if the file exists and delete it
                if os.path.exists(image_path):
                    os.remove(image_path)
        except Product.DoesNotExist:
            pass


class OrderItem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

class Order(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.TextField(default='Waiting for payment')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    address = models.TextField()
    products = models.ManyToManyField(OrderItem)
    price = models.DecimalField(default=0.00, validators=[MinValueValidator(0.0)], decimal_places=2, max_digits=10)
    email = models.EmailField(default='no@emial.com')
    paid = models.BooleanField(default=False)


class CartItem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])


class Cart(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem, blank=True)
    totalPrice = models.DecimalField(default=0.00, validators=[MinValueValidator(0.0)], decimal_places=2, max_digits=10)