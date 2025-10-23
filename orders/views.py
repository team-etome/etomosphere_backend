from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import uuid

from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderListAPIView(generics.ListAPIView):
    """API view for listing user's orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailAPIView(generics.RetrieveAPIView):
    """API view for order details"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CreateOrderAPIView(APIView):
    """API view for creating new order from cart"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create new order from cart"""
        from cart.models import Cart, CartItem
        
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate order number
        order_number = f"ETO-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total
        total_amount = sum(item.total_price for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=total_amount,
            shipping_address=request.data.get('shipping_address', ''),
            billing_address=request.data.get('billing_address', ''),
            phone=request.data.get('phone', '')
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.current_price
            )
        
        # Clear cart
        cart_items.delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateOrderStatusAPIView(APIView):
    """API view for updating order status (admin only)"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request, order_id):
        """Update order status"""
        try:
            order = Order.objects.get(id=order_id)
            new_status = request.data.get('status')
            if new_status:
                order.status = new_status
                order.save()
                return Response(OrderSerializer(order).data)
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for order management"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    serializer_class = OrderSerializer
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create new order from cart"""
        from cart.models import Cart, CartItem
        
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate order number
        order_number = f"ETO-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total
        total_amount = sum(item.total_price for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=total_amount,
            shipping_address=request.data.get('shipping_address', ''),
            billing_address=request.data.get('billing_address', ''),
            phone=request.data.get('phone', '')
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.current_price
            )
        
        # Clear cart
        cart_items.delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)