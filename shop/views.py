from django.shortcuts import render

# Create your views here.
from .tasks import send_order_created_notification

from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, status

from .models import Product, Cart, CartItem, Order, OrderItem, Notification
from .serializers import (
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    NotificationSerializer,
)


def get_or_create_cart(request):
    # Ensure session exists
    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

@api_view(['GET'])
def ping(request):
    """
    Simple health-check endpoint
    """
    return Response({"status": "ok"})




class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint to list/create/update/delete products.
    """
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer

###Cart###
class CartViewSet(viewsets.ViewSet):
    """
    /api/cart/          GET  -> get current cart
    /api/cart/clear/    POST -> clear cart
    """

    def list(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return Response({'detail': 'Cart cleared.'})

###Cart Item###
class CartItemViewSet(viewsets.ViewSet):
    """
    /api/cart-items/ POST { product_id, quantity }
    /api/cart-items/{id}/ DELETE
    """

    def create(self, request):
        cart = get_or_create_cart(request)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        cart = get_or_create_cart(request)
        try:
            item = cart.items.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in cart.'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({'detail': 'Item removed.'}, status=status.HTTP_204_NO_CONTENT)



class OrderViewSet(viewsets.ViewSet):
    """
    /api/orders/ POST -> create order from current cart
    /api/orders/ GET  -> list orders
    """

    def list(self, request):
        orders = Order.objects.all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def create(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create order
        order = Order.objects.create(
            total_price=cart.total_price,
            status='CREATED',
        )

        # Copy cart items to order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Clear cart
        cart.items.all().delete()
        send_order_created_notification.delay(order.id)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/notifications/ GET -> list notifications
    /api/notifications/{id}/ GET -> retrieve single notification
    """
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
