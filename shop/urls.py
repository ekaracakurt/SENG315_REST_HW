from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cart-item')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'notifications', views.NotificationViewSet, basename='notification')


urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('', include(router.urls)),
]
