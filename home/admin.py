from django.contrib import admin
from .models import Product, Cart, Order, CartItem, OrderItem

# Register your models here.
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(OrderItem)