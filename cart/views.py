# D:\ETMOSHPHERE\BACKEND\etomosphere_backend\cart\views.py

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from products.models import Variant  # ← changed from ProductVariant

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class AddToCartAPIView(APIView):
    """API view for adding items to cart"""

    def post(self, request):
        print(request.data, "hgjhsd")
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        print(serializer, "serializer")

        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(CartItemSerializer(cart_item).data)

        print(serializer.errors, "serializer.errors")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Get cart items for a specific user"""
        user_id = request.query_params.get('user_id')
        print(user_id, "user")

        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            cart, created = Cart.objects.get_or_create(user=user)

            # ── Updated traversal: Variant → Brand → CatalogueProduct → images ──
            cart_items = CartItem.objects.filter(cart=cart).select_related(
                'product',                          # Variant
                'product__brand',                   # Brand
                'product__brand__product',          # CatalogueProduct
            ).prefetch_related(
                'product__images',                  # VariantImage
                'product__brand__product__images',  # CatalogueProductImage
            )

            items_data = []
            for item in cart_items:
                variant = item.product  # Variant instance

                # Try variant image first, fall back to catalogue product image
                main_image = None

                variant_main = variant.images.filter(is_main=True).first()
                if variant_main:
                    main_image = variant_main.image.url
                elif variant.images.exists():
                    main_image = variant.images.first().image.url
                else:
                    # Fall back to CatalogueProduct image
                    product_main = variant.brand.product.images.filter(is_main=True).first()
                    if product_main:
                        main_image = product_main.image.url
                    elif variant.brand.product.images.exists():
                        main_image = variant.brand.product.images.first().image.url

                items_data.append({
                    'product_id': variant.id,
                    'variant_name': variant.name,
                    'brand': variant.brand.name,
                    'price': float(variant.current_price) if variant.current_price else 0,
                    'image': main_image,
                    'quantity': item.quantity,
                    'stock_status': variant.stock_status,
                })

            response_data = {
                'user_id': user_id,
                'items': items_data
            }
            print(response_data, "response_data")
            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveFromCartAPIView(APIView):
    """API view for removing items from cart"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        product_id = request.data.get('product')
        if product_id:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return Response(
                    {'error': 'Item not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response({'error': 'Product ID required'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateCartItemAPIView(APIView):
    """API view for updating cart item quantity"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
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
                return Response(
                    {'error': 'Item not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {'error': 'Product ID and quantity required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ClearCartAPIView(APIView):
    """API view for clearing all items from cart"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
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
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

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
        product_id = request.data.get('product')
        if product_id:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return Response(
                    {'error': 'Item not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response({'error': 'Product ID required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def update_item(self, request):
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
                return Response(
                    {'error': 'Item not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {'error': 'Product ID and quantity required'},
            status=status.HTTP_400_BAD_REQUEST
        )