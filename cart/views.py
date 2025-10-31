from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from products.models import ProductVariant

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


# class CartDetailAPIView(generics.RetrieveAPIView):
#     """API view for getting user's cart"""
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self):
#         cart, created = Cart.objects.get_or_create(user=self.request.user)
#         return cart


class AddToCartAPIView(APIView):
    """API view for adding items to cart"""
    # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        print(request.data,"hgjhsd")
        """Add item to cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        print(serializer,"serializer")
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data)
        print(serializer.errors,"serializer.errors")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        """Get cart items for a specific user"""
        user_id = request.query_params.get('user_id')

        print(user_id,"user")
        
        if not user_id:
            return Response({'error': 'user_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get or create cart for the user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            cart, created = Cart.objects.get_or_create(user=user)
            
            # Get all cart items with product details and images
            cart_items = CartItem.objects.filter(cart=cart).select_related(
                'product', 
                'product__product_model', 
                'product__product_model__brand'
            ).prefetch_related(
                'product__product_model__images'
            )
            
            # Create simplified response with only product image, price, and product ID
            items_data = []
            for item in cart_items:
                # Get main image or first image
                main_image = None
                if item.product.product_model.images.exists():
                    main_img = item.product.product_model.images.filter(is_main=True).first()
                    if main_img:
                        main_image = main_img.image.url
                    else:
                        main_image = item.product.product_model.images.first().image.url
                
                items_data.append({
                    'product_id': item.product.id,
                    'price': float(item.product.price) if item.product.price else 0,
                    'image': main_image,
                    'quantity': item.quantity
                })
            
            response_data = {
                'user_id': user_id,
                'items': items_data
            }

            


            print(response_data,"response_data")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class RemoveFromCartAPIView(APIView):
    """API view for removing items from cart"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        """Remove item from cart"""
        product_id = request.data.get('product')
        if product_id:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Product ID required'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateCartItemAPIView(APIView):
    """API view for updating cart item quantity"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        """Update item quantity in cart"""
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')
        
        if product_id and quantity:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                cart_item.quantity = quantity
                cart_item.save()
                return Response(CartItemSerializer(cart_item).data)
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Product ID and quantity required'}, status=status.HTTP_400_BAD_REQUEST)


class ClearCartAPIView(APIView):
    """API view for clearing all items from cart"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        """Clear all items from cart"""
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared successfully'})


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for shopping cart management"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['add_item', 'remove_item', 'update_item']:
            return CartItemSerializer
        return CartSerializer
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """Get current user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove item from cart"""
        product_id = request.data.get('product')
        if product_id:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Product ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """Update item quantity in cart"""
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')
        
        if product_id and quantity:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                cart_item.quantity = quantity
                cart_item.save()
                return Response(CartItemSerializer(cart_item).data)
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Product ID and quantity required'}, status=status.HTTP_400_BAD_REQUEST)