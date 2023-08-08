from django.forms import ModelForm
from .models import Product, Order

class productForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']

class orderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']
