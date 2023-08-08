from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.IndexView.as_view(), name='main'),
    path('login/', views.loginView.as_view(), name='login'),
    path('logout/', views.logoutView.as_view(), name='logout'),
    path('product/<int:pk>', views.productView.as_view(), name='product'),
    path('addProduct/', views.addProduct.as_view(), name='add-product'),
    path('cart/', views.cartView.as_view(), name='cart'),
    path('addToCart/<int:pk>', views.addToCart, name='add-to-cart'),
    path('removeFromCart/<int:pk>', views.removeFromCart, name='remove-from-cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order_success/', views.OrderSuccessView.as_view(), name='order_success'),
    path('order/', views.orderView.as_view(), name='order'),
    path('allOrder/', views.allOrderView.as_view(), name='all-order'),
    path('updateOrder/<int:pk>', views.orderUpdate.as_view(), name='update-order'),
    path('editProduct/<int:pk>', views.editProduct.as_view(), name='edit-product'),
    path('dashboard/', views.dashboardView.as_view(), name='admin-dashboard'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('payment/<int:pk>', views.payment, name='payment'),
    path('paypal-reverse', views.paypal_reverse, name='paypal-reverse'),
    path('paypal-cancel', views.paypal_cancel, name='paypal-cancel'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)