from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from products.models import *
from django.db import transaction
import json


ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_IMAGE_BYTES = 30 * 1024 * 1024  # 30MB

def _str_to_bool(v):
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

class AddProduct(APIView):
    def post(self, request):
        print("entereddddd")
        try:
            data = request.data
            print("📦 Received product data:", data)

            # ---------- STEP 1: REQUIRED FIELDS ----------
            required_fields = ['category_slug', 'category_name', 'brand_name', 'product_name', 'variant_name', 'price']
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return Response({'error': 'Missing required fields', 'missing_fields': missing_fields}, status=400)

            # ---------- STEP 2: VALIDATION ----------
            validation_errors = []

            # price
            price = data.get('price')
            try:
                price_decimal = float(price) if price else None
                if price_decimal is not None and price_decimal < 0:
                    validation_errors.append("Price cannot be negative")
            except (ValueError, TypeError):
                validation_errors.append("Invalid price format")

            # JSON specs
            product_spec_json = data.get('product_spec_json', '{}')
            if isinstance(product_spec_json, str):
                try:
                    product_spec_json = json.loads(product_spec_json)
                except json.JSONDecodeError:
                    validation_errors.append("Invalid product_spec_json format")

            variant_spec_json = data.get('variant_spec_json', '{}')
            if isinstance(variant_spec_json, str):
                try:
                    variant_spec_json = json.loads(variant_spec_json)
                except json.JSONDecodeError:
                    validation_errors.append("Invalid variant_spec_json format")

            # enums
            lifecycle_status = data.get('lifecycle_status', 'active')
            if lifecycle_status not in ['active', 'discontinued', 'end_of_life']:
                validation_errors.append("Invalid lifecycle_status. Must be one of: ['active', 'discontinued', 'end_of_life']")

            stock_status = data.get('stock_status', 'in_stock')
            if stock_status not in ['in_stock', 'out_of_stock']:
                validation_errors.append("Invalid stock_status. Must be one of: ['in_stock', 'out_of_stock']")

            currency = data.get('currency', 'INR')
            if not isinstance(currency, str) or len(currency) != 3:
                validation_errors.append("Currency must be 3 characters (e.g., INR, USD)")

            # Files: category (single)
            category_image = request.FILES.get('category_image')

            if category_image:
                if category_image.size > MAX_IMAGE_BYTES:
                    validation_errors.append("Category image size must be less than 30MB")
                if category_image.content_type not in ALLOWED_IMAGE_TYPES:
                    validation_errors.append("Category image must be JPEG, PNG, WebP, or GIF")

            # Files: product (multiple)
            product_images = request.FILES.getlist('product_images') or request.FILES.getlist('product_images[]')

            # Validate each product file
            for f in product_images:
                if f.size > MAX_IMAGE_BYTES:
                    validation_errors.append(f"Product image '{f.name}' exceeds 30MB")
                if f.content_type not in ALLOWED_IMAGE_TYPES:
                    validation_errors.append(f"Product image '{f.name}' must be JPEG, PNG, WebP, or GIF")

            if validation_errors:
                return Response({'error': 'Validation failed', 'validation_errors': validation_errors}, status=400)

            print("✅ All validations passed, proceeding with database operations...")

            # ---------- STEP 3: DB SAVE (ATOMIC) ----------
            with transaction.atomic():
                # Category
                category, _ = Category.objects.get_or_create(
                    slug=data.get('category_slug'),
                    defaults={'name': data.get('category_name'), 'description': data.get('category_description', '')}
                )
                print(f"✅ Category: Found - {category.name}")

                # Brand
                brand, _ = Brand.objects.get_or_create(
                    name=data.get('brand_name'),
                    category=category,
                    defaults={'website': data.get('brand_website', '')}
                )
                print(f"✅ Brand: Found - {brand.name}")

                # ProductModel (consider get_or_create if duplicates possible)
                product_model = ProductModel.objects.create(
                    brand=brand,
                    name=data.get('product_name'),
                    short_code=data.get('product_short_code', ''),
                    description=data.get('product_description', ''),
                    lifecycle_status=lifecycle_status,
                    spec_json=product_spec_json
                )
                print(f"✅ ProductModel Created: {product_model.name}")

                # Variant
                product_variant = ProductVariant.objects.create(
                    product_model=product_model,
                    variant_name=data.get('variant_name'),
                    sku=data.get('sku', ''),
                    mpn=data.get('mpn', ''),
                    upc=data.get('upc', ''),
                    status=data.get('variant_status', 'active'),
                    price=price_decimal,
                    currency=currency,
                    stock_status=stock_status,
                    spec_json=variant_spec_json
                )
                print(f"✅ ProductVariant Created: {product_variant.variant_name}")

                # Category image (single)
                print(f"🔍 Category Image Check: {category_image}")
                if category_image:
                    print(f"📁 Category Image Details: {category_image.name}, Size: {category_image.size}, Type: {category_image.content_type}")
                    cat_img = CategoryImage.objects.create(
                        category=category,
                        image=category_image,
                        is_main=True
                    )
                    print(f"✅ Category Image Created: {cat_img.image.name}")
                else:
                    print("❌ No category image provided")

                # Product images (MULTIPLE) — FK uses ProductModel
                if product_images:
                    print(f"🔍 Product Images Count: {len(product_images)}")

                    any_marked_main = False
                    saved_images = []

                    for idx, f in enumerate(product_images):
                        # Optional: per-image metadata from the form
                        # name these fields like image_alt_text_0 / is_main_image_0, etc.
                        alt_text = data.get(f'image_alt_text_{idx}', '') or product_model.name
                        is_main = _str_to_bool(data.get(f'is_main_image_{idx}', 'false'))

                        if is_main:
                            any_marked_main = True

                        pi = ProductImage.objects.create(
                            product=product_model,  # <-- correct FK to ProductModel
                            image=f,
                            alt_text=alt_text,
                            is_main=is_main
                        )
                        saved_images.append({'id': pi.id, 'name': pi.image.name, 'is_main': pi.is_main})

                    # If none marked as main, set first as main
                    if not any_marked_main:
                        first = ProductImage.objects.filter(product=product_model).order_by('id').first()
                        if first and not first.is_main:
                            first.is_main = True
                            first.save(update_fields=['is_main'])
                            # update saved_images record too
                            for rec in saved_images:
                                if rec['id'] == first.id:
                                    rec['is_main'] = True
                                    break

                    print(f"✅ Saved product images: {saved_images}")
                else:
                    print("❌ No product image provided")

            # ---------- STEP 4: RESPONSE ----------
            # Get category images for response
            category_images_response = []
            for cat_img in category.images.all():
                category_images_response.append({
                    'id': cat_img.id,
                    'image_url': cat_img.image.url if cat_img.image else None,
                    'is_main': cat_img.is_main,
                    'created_at': cat_img.created_at.isoformat()
                })
            
            # Get product images for response
            product_images_response = []
            for prod_img in product_model.images.all():
                product_images_response.append({
                    'id': prod_img.id,
                    'image_url': prod_img.image.url if prod_img.image else None,
                    'alt_text': prod_img.alt_text,
                    'is_main': prod_img.is_main,
                    'created_at': prod_img.created_at.isoformat()
                })
            
            return Response({
                'message': 'Product created successfully',
                'data': {
                    'category': {
                        'id': category.id, 
                        'name': category.name, 
                        'slug': category.slug,
                        'description': category.description,
                        'images': category_images_response
                    },
                    'brand': {
                        'id': brand.id, 
                        'name': brand.name,
                        'website': brand.website
                    },
                    'product_model': {
                        'id': product_model.id, 
                        'name': product_model.name,
                        'short_code': product_model.short_code,
                        'description': product_model.description,
                        'lifecycle_status': product_model.lifecycle_status,
                        'images': product_images_response
                    },
                    'product_variant': {
                        'id': product_variant.id,
                        'variant_name': product_variant.variant_name,
                        'sku': product_variant.sku,
                        'mpn': product_variant.mpn,
                        'upc': product_variant.upc,
                        'price': str(product_variant.price) if product_variant.price is not None else None,
                        'currency': product_variant.currency,
                        'stock_status': product_variant.stock_status
                    }
                }
            }, status=201)

        except Exception as e:
            print(f"❌ Error creating product: {str(e)}")
            return Response({'error': 'Failed to create product', 'details': str(e)}, status=400)

    
    def get(self, request):
        """Get all products with their related data"""
        try:
            # Get all ProductModels with related data
            products = ProductModel.objects.select_related('brand__category').prefetch_related(
                'productvariant_set', 'images', 'brand__category__images'
            ).all()
            
            products_data = []
            
            for product in products:
                # Get all variants for this product
                variants_data = []
                for variant in product.productvariant_set.all():
                    variants_data.append({
                        'id': variant.id,
                        'variant_name': variant.variant_name,
                        'sku': variant.sku,
                        'mpn': variant.mpn,
                        'upc': variant.upc,
                        'status': variant.status,
                        'price': str(variant.price) if variant.price else None,
                        'sale_price': str(variant.sale_price) if variant.sale_price else None,
                        'cost_price': str(variant.cost_price) if variant.cost_price else None,
                        'currency': variant.currency,
                        'is_on_sale': variant.is_on_sale,
                        'stock_status': variant.stock_status,
                        'current_price': str(variant.current_price) if variant.current_price else None,
                        'discount_percentage': variant.discount_percentage,
                        'profit_margin': variant.profit_margin,
                        'spec_json': variant.spec_json,
                        'created_at': variant.created_at.isoformat(),
                        'updated_at': variant.updated_at.isoformat()
                    })
                
                # Get all images for this product
                images_data = []
                product_images = product.images.all()
                print(f"🔍 Product: {product.name} - Found {product_images.count()} images")
                
                for image in product_images:
                    print(f"📷 Product Image: {image.id} - {image.image.name if image.image else 'No image'}")
                    images_data.append({
                        'id': image.id,
                        'image_url': image.image.url if image.image else None,
                        'alt_text': image.alt_text,
                        'is_main': image.is_main,
                        'created_at': image.created_at.isoformat()
                    })

                    
                
                # Get all images for the category
                category_images_data = []
                category_images = product.brand.category.images.all()
                print(f"🔍 Category: {product.brand.category.name} - Found {category_images.count()} images")
                
                for cat_image in category_images:
                    print(f"📷 Category Image: {cat_image.id} - {cat_image.image.name if cat_image.image else 'No image'}")
                    category_images_data.append({
                        'id': cat_image.id,
                        'image_url': cat_image.image.url if cat_image.image else None,
                        'is_main': cat_image.is_main,
                        'created_at': cat_image.created_at.isoformat()
                    })
                
                # Build product data
                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'short_code': product.short_code,
                    'description': product.description,
                    'lifecycle_status': product.lifecycle_status,
                    'spec_json': product.spec_json,
                    'brand': {
                        'id': product.brand.id,
                        'name': product.brand.name,
                        'website': product.brand.website,
                        'category': {
                            'id': product.brand.category.id,
                            'name': product.brand.category.name,
                            'slug': product.brand.category.slug,
                            'description': product.brand.category.description,
                            'images': category_images_data
                        }
                    },
                    'variants': variants_data,
                    'product_images': images_data,
                    'created_at': product.created_at.isoformat(),
                    'updated_at': product.updated_at.isoformat()
                }
                
                products_data.append(product_data)

                print(product_data,"eeee")
            
            return Response({
                'message': 'Products retrieved successfully',
                'count': len(products_data),
                'products': products_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Error retrieving products: {str(e)}")
            return Response({
                'error': 'Failed to retrieve products',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)