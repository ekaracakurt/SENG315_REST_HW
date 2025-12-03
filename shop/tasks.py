from celery import shared_task
from .models import Order, Notification


@shared_task
def send_order_created_notification(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    message = f"Order #{order.id} has been created with total {order.total_price}."
    Notification.objects.create(
        order=order,
        type='ORDER_CREATED',
        message=message,
    )
