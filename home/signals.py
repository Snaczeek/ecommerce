from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver

from .models import Order

@receiver(valid_ipn_received)
def valid_payment(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        order_id = ipn.invoice
        order = Order.objects.get(id=order_id)
        order.paid = True
        order.status = "Pending"
        order.save()

@receiver(invalid_ipn_received)
def invalid_payment(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        order_id = ipn.invoice
        order = Order.objects.get(id=order_id)
        order.paid = True
        order.status = "Pending"
        order.save()
