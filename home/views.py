# from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views import View
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login

from django.conf import settings

from .forms import productForm, orderForm
from paypal.standard.forms import PayPalPaymentsForm

from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm

from .models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User
from django.db.models import Sum

# Create your views here.
def user_is_admin(user):
    return user.is_authenticated and user.is_superuser

class IndexView(View):
    template_name = 'home/main.html'
    paginate_by = 8

    def get(self, request):
        sort_by = request.GET.get('sort', '')

        queryset = Product.objects.all()

        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'alphabetical':
            queryset = queryset.order_by('name')

        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {'product': page_obj})


class AdminDashboardMixin(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics data
        context['user_count'] = User.objects.count()
        context['product_count'] = Product.objects.count()
        context['order_count'] = Order.objects.count()
        context['total_amount'] = Order.objects.aggregate(Sum('price'))['price__sum']
        
        return context

@method_decorator(user_passes_test(user_is_admin), name='dispatch')
class dashboardView(AdminDashboardMixin, ListView):
    model = Product
    template_name = 'home/dashboard.html'

    
@method_decorator(login_required, name='dispatch')
class cartView(ListView):
    model = Cart
    template_name = 'home/cart.html'
    context_object_name = 'cart'

    def get_queryset(self):
        return Cart.objects.filter(owner__id = self.request.user.id)

@method_decorator(login_required, name='dispatch')
class orderView(ListView):
    model = Order
    template_name = 'home/order.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(owner = self.request.user).order_by('-created')
    
@method_decorator(user_passes_test(user_is_admin), name='dispatch')
class allOrderView(ListView):
    model = Order
    template_name = 'home/order.html'
    context_object_name = 'order'

    # Order by newest orders
    def get_queryset(self):
        return Order.objects.all().order_by('-created')

@method_decorator(user_passes_test(user_is_admin), name='dispatch')
class orderUpdate(UpdateView):
    model =  Order
    fields = ['status']
    template_name = 'home/orderUpdate.html'
    success_url = reverse_lazy('all-order')

@login_required
def addToCart(request, pk):
    try:
        cart = Cart.objects.get(owner__id = request.user.id)
    except Exception:
        return HttpResponse('user doesnt have cart object')
    
    # Checking if user already have product in cart
    if CartItem.objects.filter(owner__id = request.user.id, product__id = pk).exists():
        cartItem = CartItem.objects.get(owner__id = request.user.id, product__id = pk)
        cartItem.quantity += 1
        cartItem.save()
        cart.totalPrice += cartItem.product.price
        cart.save()
        return redirect('cart')
    else:
        # Creating cartItem
        product = Product.objects.get(id = pk)
        cartItem = CartItem(owner = request.user, product = product, quantity = 1)
        cartItem.save()
        # Adding item to cart
        cart.items.add(cartItem)
        cart.totalPrice += cartItem.product.price
        cart.save()
        return redirect('cart')

@login_required
def removeFromCart(request, pk):
    try:
        cart = Cart.objects.get(owner__id = request.user.id)
    except Exception:
        return HttpResponse('user doesnt have cart object')
    
    # Checking if user have product in cart
    if cart.items.filter(id = pk).exists():
        cartItem = CartItem.objects.get(id = pk)
        # Checking if there is more than 1 same product
        if cartItem.quantity > 1:
            cartItem.quantity -= 1
            cartItem.save()
            cart.totalPrice -= cartItem.product.price
            cart.save()
            return redirect('cart')
        else:
            # Deleting item
            cart.totalPrice -= cartItem.product.price
            cart.save()
            cartItem.delete()
            return redirect('cart')
            

    else:
        return HttpResponse('Item doesnt exist')

class productView(DetailView):
    model = Product
    template_name = 'home/detail.html'
    context_object_name = 'product'


@method_decorator(user_passes_test(user_is_admin), name='dispatch')
class addProduct(CreateView):
    model = Product
    template_name = 'home/create.html'
    form_class = productForm
    success_url = reverse_lazy('main')

@method_decorator(user_passes_test(user_is_admin), name='dispatch')
class editProduct(UpdateView):
    model = Product
    fields = '__all__'
    template_name = 'home/editProduct.html'
    success_url = reverse_lazy('main')

class loginView(LoginView):
    template_name = 'home/login.html'
    success_url = reverse_lazy('main')

class logoutView(LogoutView):
    next_page = reverse_lazy('main')

@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    template_name = 'home/checkout.html'

    def get(self, request):
        cart_items = CartItem.objects.filter(owner=request.user)
        total_price = sum(item.quantity * item.product.price for item in cart_items)
        return render(request, self.template_name, {'cart_items': cart_items, 'total_price': total_price})
    
    def post(self, request):
        address = request.POST.get('address', '')
        email = request.POST.get('email', '')
        if address and email:
            # Create the order and order items
            cart_items = CartItem.objects.filter(owner=request.user)
            cart = Cart.objects.get(owner=request.user)
            if len(cart_items) == 0:
                return HttpResponse("No items in cart")            
            total_price = sum(item.quantity * item.product.price for item in cart_items)
            order = Order.objects.create(owner=request.user, address=address, price=total_price, email = email)
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(owner=request.user, product=cart_item.product, quantity=cart_item.quantity)
                order.products.add(order_item)
            # Clear the cart after successful checkout
            cart_items.delete()
            cart.totalPrice = 0.00
            cart.save()
            return redirect(f'../payment/{order.id}')
        else:
            return redirect('checkout')


class OrderSuccessView(View):
    template_name = 'home/order_success.html'

    def get(self, request):
        return render(request, self.template_name)
    
class RegistrationView(View):
    template_name = 'home/register.html'
    
    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Create Cart instance for the user
                Cart.objects.create(owner=user)
                return redirect('main')
        return render(request, self.template_name, {'form': form})

@login_required
def payment(request, pk):
    host = request.get_host()
    # Getting order object
    try:
        order = Order.objects.get(id = pk)
    except Exception:
        return redirect('main')
    # Checking if its user's order
    if not order.owner == request.user:
        return redirect('main')
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': f'{order.price}',
        'item_name': 'Order',
        'invoice': f'{order.id}',
        'currency_code': 'PLN',
        'notify_url': f'http://{host}{reverse("paypal-ipn")}',
        'return_url': f'http://{host}{reverse("paypal-reverse")}',
        'cancel_return': f'http://{host}{reverse("paypal-cancel")}',
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {'form': form}
    return render(request, 'home/payment.html', context)

# fires off on successful payment
def paypal_reverse(request):
    return redirect('order_success')

# fires off on unsuccessful payment
def paypal_cancel(request):
    return redirect('main')
