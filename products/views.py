# D:\ETMOSHPHERE\BACKEND\etomosphere_backend\products\views.py

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
import json

from products.models import (
    Category, CategoryImage,
    CatalogueProduct, CatalogueProductImage,
    Brand,
    Variant, VariantImage
)


ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_IMAGE_BYTES = 30 * 1024 * 1024  # 30MB


def _str_to_bool(v):
    return str(v).strip().lower() in {"1", "true", "yes", "on"}


# ──────────────────────────────────────────────────────────────
# ADD PRODUCT
# ──────────────────────────────────────────────────────────────

class AddProduct(APIView):

    def post(self, request):
        print("entered AddProduct POST")
        try:
            data = request.data
            print("📦 Received product data:", data)

            # ── Required fields ──
            required_fields = [
                'category_slug',    # Eg: "hardware"
                'category_name',    # Eg: "Hardware"
                'product_name',     # Eg: "Interactive Display"
                'product_slug',     # Eg: "interactive-display"
                'brand_name',       # Eg: "BenQ"
                'variant_name',     # Eg: "RP8603 65 inch"
                'price'
            ]
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return Response(
                    {'error': 'Missing required fields', 'missing_fields': missing_fields},
                    status=400
                )

            # ── Validation ──
            validation_errors = []

            price = data.get('price')
            try:
                price_decimal = float(price) if price else None
                if price_decimal is not None and price_decimal < 0:
                    validation_errors.append("Price cannot be negative")
            except (ValueError, TypeError):
                validation_errors.append("Invalid price format")

            spec_json = data.get('spec_json', '{}')
            if isinstance(spec_json, str):
                try:
                    spec_json = json.loads(spec_json)
                except json.JSONDecodeError:
                    validation_errors.append("Invalid spec_json format")

            lifecycle_status = data.get('lifecycle_status', 'active')
            if lifecycle_status not in ['active', 'discontinued', 'end_of_life']:
                validation_errors.append("Invalid lifecycle_status")

            stock_status = data.get('stock_status', 'in_stock')
            if stock_status not in ['in_stock', 'out_of_stock']:
                validation_errors.append("Invalid stock_status")

            currency = data.get('currency', 'INR')
            if not isinstance(currency, str) or len(currency) != 3:
                validation_errors.append("Currency must be 3 characters (eg: INR, USD)")

            category_image = request.FILES.get('category_image')
            if category_image:
                if category_image.size > MAX_IMAGE_BYTES:
                    validation_errors.append("Category image must be less than 30MB")
                if category_image.content_type not in ALLOWED_IMAGE_TYPES:
                    validation_errors.append("Category image must be JPEG, PNG, WebP, or GIF")

            product_images = (
                request.FILES.getlist('product_images') or
                request.FILES.getlist('product_images[]')
            )
            for f in product_images:
                if f.size > MAX_IMAGE_BYTES:
                    validation_errors.append(f"Product image '{f.name}' exceeds 30MB")
                if f.content_type not in ALLOWED_IMAGE_TYPES:
                    validation_errors.append(f"Product image '{f.name}' must be JPEG, PNG, WebP, or GIF")

            variant_images = (
                request.FILES.getlist('variant_images') or
                request.FILES.getlist('variant_images[]')
            )
            for f in variant_images:
                if f.size > MAX_IMAGE_BYTES:
                    validation_errors.append(f"Variant image '{f.name}' exceeds 30MB")
                if f.content_type not in ALLOWED_IMAGE_TYPES:
                    validation_errors.append(f"Variant image '{f.name}' must be JPEG, PNG, WebP, or GIF")

            if validation_errors:
                return Response(
                    {'error': 'Validation failed', 'validation_errors': validation_errors},
                    status=400
                )

            # ── DB Save ──
            with transaction.atomic():

                # Level 1 — Category
                category, _ = Category.objects.get_or_create(
                    slug=data.get('category_slug'),
                    defaults={
                        'name': data.get('category_name'),
                        'description': data.get('category_description', ''),
                        # solution must be passed if creating new category
                        # pass solution_id in request if needed
                    }
                )
                print(f"✅ Category: {category.name}")

                # Category image
                if category_image:
                    CategoryImage.objects.create(
                        category=category,
                        image=category_image,
                        is_main=True
                    )

                # Level 2 — CatalogueProduct
                catalogue_product, _ = CatalogueProduct.objects.get_or_create(
                    slug=data.get('product_slug'),
                    defaults={
                        'category': category,
                        'name': data.get('product_name'),
                        'description': data.get('product_description', ''),
                    }
                )
                print(f"✅ CatalogueProduct: {catalogue_product.name}")

                # Product images
                if product_images:
                    any_marked_main = False
                    for idx, f in enumerate(product_images):
                        alt_text = data.get(f'product_image_alt_{idx}', '') or catalogue_product.name
                        is_main = _str_to_bool(data.get(f'product_image_main_{idx}', 'false'))
                        if is_main:
                            any_marked_main = True
                        CatalogueProductImage.objects.create(
                            product=catalogue_product,
                            image=f,
                            alt_text=alt_text,
                            is_main=is_main
                        )
                    if not any_marked_main:
                        first = CatalogueProductImage.objects.filter(
                            product=catalogue_product
                        ).order_by('id').first()
                        if first:
                            first.is_main = True
                            first.save(update_fields=['is_main'])

                # Level 3 — Brand
                brand, _ = Brand.objects.get_or_create(
                    name=data.get('brand_name'),
                    product=catalogue_product,
                    defaults={'website': data.get('brand_website', '')}
                )
                print(f"✅ Brand: {brand.name}")

                # Level 4 — Variant
                variant = Variant.objects.create(
                    brand=brand,
                    name=data.get('variant_name'),
                    sku=data.get('sku', ''),
                    mpn=data.get('mpn', ''),
                    description=data.get('variant_description', ''),
                    spec_json=spec_json,
                    price=price_decimal,
                    sale_price=data.get('sale_price') or None,
                    cost_price=data.get('cost_price') or None,
                    currency=currency,
                    is_on_sale=_str_to_bool(data.get('is_on_sale', 'false')),
                    stock_status=stock_status,
                    lifecycle_status=lifecycle_status,
                )
                print(f"✅ Variant: {variant.name}")

                # Variant images
                if variant_images:
                    any_marked_main = False
                    for idx, f in enumerate(variant_images):
                        alt_text = data.get(f'variant_image_alt_{idx}', '') or variant.name
                        is_main = _str_to_bool(data.get(f'variant_image_main_{idx}', 'false'))
                        if is_main:
                            any_marked_main = True
                        VariantImage.objects.create(
                            variant=variant,
                            image=f,
                            alt_text=alt_text,
                            is_main=is_main
                        )
                    if not any_marked_main:
                        first = VariantImage.objects.filter(variant=variant).order_by('id').first()
                        if first:
                            first.is_main = True
                            first.save(update_fields=['is_main'])

            return Response({'message': 'Product created successfully'}, status=201)

        except Exception as e:
            print(f"❌ Error creating product: {str(e)}")
            return Response({'error': 'Failed to create product', 'details': str(e)}, status=400)


# ──────────────────────────────────────────────────────────────
# LIST PRODUCTS
# ──────────────────────────────────────────────────────────────

class ListProducts(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            categories = Category.objects.select_related(
                'solution'
            ).prefetch_related(
                'images',
                'catalogue_products__brands__variants__images',
                'catalogue_products__images',
            ).all()

            data = []

            for category in categories:
                category_data = {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'solution': category.solution.name if category.solution else None,
                    'images': [
                        {'image_url': img.image.url, 'is_main': img.is_main}
                        for img in category.images.all()
                    ],
                    'products': []
                }

                for product in category.catalogue_products.all():
                    product_data = {
                        'id': product.id,
                        'name': product.name,
                        'slug': product.slug,
                        'description': product.description,
                        'images': [
                            {'image_url': img.image.url, 'is_main': img.is_main, 'alt_text': img.alt_text}
                            for img in product.images.all()
                        ],
                        'brands': []
                    }

                    for brand in product.brands.all():
                        brand_data = {
                            'id': brand.id,
                            'name': brand.name,
                            'website': brand.website,
                            'variants': []
                        }

                        for variant in brand.variants.all():
                            brand_data['variants'].append({
                                'id': variant.id,
                                'name': variant.name,
                                'sku': variant.sku,
                                'mpn': variant.mpn,
                                'description': variant.description,
                                'spec_json': variant.spec_json,
                                'price': str(variant.price) if variant.price else None,
                                'sale_price': str(variant.sale_price) if variant.sale_price else None,
                                'current_price': str(variant.current_price) if variant.current_price else None,
                                'currency': variant.currency,
                                'is_on_sale': variant.is_on_sale,
                                'discount_percentage': variant.discount_percentage,
                                'stock_status': variant.stock_status,
                                'lifecycle_status': variant.lifecycle_status,
                                'images': [
                                    {'image_url': img.image.url, 'is_main': img.is_main}
                                    for img in variant.images.all()
                                ]
                            })

                        product_data['brands'].append(brand_data)

                    category_data['products'].append(product_data)

                data.append(category_data)

            return Response({'count': len(data), 'categories': data}, status=200)

        except Exception as e:
            print(f"❌ Error listing products: {str(e)}")
            return Response({'error': 'Failed to retrieve products', 'details': str(e)}, status=500)


from django.shortcuts import get_object_or_404
 
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
 
from .models import CatalogueProduct, Variant
class ProductDetailView(APIView):
    """
    GET /api/products/<id>/
    GET /api/products/<id>/?type=variant   → resolve by Variant PK
    GET /api/products/<id>/?type=product   → resolve by CatalogueProduct PK (default)

    Returns a full product detail payload that matches what ProductDetail.jsx expects:
    {
        id, name, slug, description,
        category: { id, name, slug, solution_name, solution_slug },
        images: [ { id, image_url, is_main, alt_text } ],
        brands: [
            {
                id, name, logo, website,
                variants: [
                    {
                        id, name, sku, mpn, description,
                        spec_json, price, sale_price, current_price,
                        currency, is_on_sale, discount_percentage,
                        stock_status, lifecycle_status, is_focused,
                        images: [ { id, image_url, is_main, alt_text } ]
                    }
                ]
            }
        ],
        price_summary: { min, max, currency } | null,
        focused_variant_id: int | null,
        related_products: [ { id, name, slug, image } ]
    }
    """

    permission_classes = [AllowAny]

    def get(self, request, product_id):
        lookup_type = request.query_params.get('type', 'product')
        focused_variant_id = None

        try:
            # ── 1. Resolve the CatalogueProduct ──────────────────────────────
            if lookup_type == 'variant':
                variant = get_object_or_404(
                    Variant.objects.select_related('brand', 'catalogue_product'),
                    pk=product_id,
                )
                focused_variant_id = variant.id

                # Prefer the direct catalogue_product FK first (new approach)
                if variant.catalogue_product:
                    catalogue_product = (
                        CatalogueProduct.objects
                        .filter(pk=variant.catalogue_product_id)
                        .select_related('category__solution')
                        .prefetch_related('images', 'brands')
                        .first()
                    )
                else:
                    # Fallback: Brand → CatalogueProduct via M2M (old approach)
                    catalogue_product = (
                        CatalogueProduct.objects
                        .filter(brands=variant.brand)
                        .select_related('category__solution')
                        .prefetch_related('images', 'brands')
                        .first()
                    )

                if not catalogue_product:
                    return Response(
                        {'error': 'No catalogue product found for this variant.'},
                        status=404,
                    )

            else:
                # Default: product_id IS a CatalogueProduct id
                catalogue_product = get_object_or_404(
                    CatalogueProduct.objects
                    .select_related('category__solution')
                    .prefetch_related('images', 'brands'),
                    pk=product_id,
                )

            # ── 2. Category + Solution ────────────────────────────────────────
            category = catalogue_product.category
            solution = category.solution if category else None

            # ── 3. Brands → Variants (scoped to THIS catalogue_product) ───────
            brands_data = []
            all_prices  = []

            for brand in catalogue_product.brands.all():

                # KEY FIX: filter variants by BOTH brand AND catalogue_product
                # This ensures Product A (Cybernetyx) and Product B (Cybernetyx)
                # each show only their own variants, not all Cybernetyx variants.
                brand_variants = Variant.objects.filter(
                    brand=brand,
                    catalogue_product=catalogue_product,
                ).prefetch_related('images').order_by('sort_order', 'name')

                # Fallback: if no variants are linked via catalogue_product FK yet
                # (i.e. before migration data is filled), fall back to all brand variants.
                # Remove this fallback once all fixtures are updated with catalogue_product.
                brand_variants = Variant.objects.filter(
    brand=brand,
    catalogue_product=catalogue_product,
).prefetch_related('images').order_by('sort_order', 'name')


                variants_data = []

                for v in brand_variants:
                    price         = float(v.price)         if v.price         else None
                    sale_price    = float(v.sale_price)    if v.sale_price    else None
                    current_price = float(v.current_price) if v.current_price else None

                    if current_price is not None:
                        all_prices.append(current_price)

                    # Variant images — build absolute URLs
                    variant_images = []
                    for img in v.images.all():
                        try:
                            url = request.build_absolute_uri(img.image.url) if img.image else None
                        except Exception:
                            url = None
                        variant_images.append({
                            'id':        img.id,
                            'image_url': url,
                            'is_main':   img.is_main,
                            'alt_text':  img.alt_text,
                        })

                    variants_data.append({
                        'id':                  v.id,
                        'name':                v.name,
                        'sku':                 v.sku,
                        'mpn':                 v.mpn,
                        'description':         v.description,
                        'spec_json':           v.spec_json or {},
                        'price':               price,
                        'sale_price':          sale_price,
                        'current_price':       current_price,
                        'currency':            v.currency,
                        'is_on_sale':          v.is_on_sale,
                        'discount_percentage': v.discount_percentage,
                        'stock_status':        v.stock_status,
                        'lifecycle_status':    v.lifecycle_status,
                        'is_focused':          (v.id == focused_variant_id),
                        'images':              variant_images,
                    })

                # Brand logo — absolute URL
                try:
                    logo_url = request.build_absolute_uri(brand.logo.url) if brand.logo else None
                except Exception:
                    logo_url = None

                brands_data.append({
                    'id':       brand.id,
                    'name':     brand.name,
                    'logo':     logo_url,
                    'website':  brand.website,
                    'variants': variants_data,
                })

            # ── 4. Product-level images ───────────────────────────────────────
            product_images = []
            for img in catalogue_product.images.all():
                try:
                    url = request.build_absolute_uri(img.image.url) if img.image else None
                except Exception:
                    url = None
                product_images.append({
                    'id':        img.id,
                    'image_url': url,
                    'is_main':   img.is_main,
                    'alt_text':  img.alt_text,
                })

            # ── 5. Price summary ──────────────────────────────────────────────
            price_summary = None
            if all_prices:
                price_summary = {
                    'min':      min(all_prices),
                    'max':      max(all_prices),
                    'currency': 'INR',
                }

            # ── 6. Related products (same category, excluding self) ────────────
            related_qs = (
                CatalogueProduct.objects
                .filter(category=category)
                .exclude(pk=catalogue_product.pk)
                .prefetch_related('images')
                [:6]
            )

            related = []
            for rp in related_qs:
                img = rp.images.filter(is_main=True).first() or rp.images.first()
                try:
                    img_url = request.build_absolute_uri(img.image.url) if img and img.image else None
                except Exception:
                    img_url = None

                related.append({
                    'id':    rp.id,
                    'name':  rp.name,
                    'slug':  rp.slug,
                    'image': img_url,
                })

            # ── 7. Build final payload ────────────────────────────────────────
            payload = {
                'id':          catalogue_product.id,
                'name':        catalogue_product.name,
                'slug':        catalogue_product.slug,
                'description': catalogue_product.description,
                'sort_order':  catalogue_product.sort_order,
                'created_at':  catalogue_product.created_at.isoformat(),
                'updated_at':  catalogue_product.updated_at.isoformat(),

                'category': {
                    'id':            category.id,
                    'name':          category.name,
                    'slug':          category.slug,
                    'description':   category.description,
                    'solution_name': solution.name if solution else None,
                    'solution_slug': solution.slug if solution else None,
                } if category else None,

                'images':             product_images,
                'brands':             brands_data,
                'price_summary':      price_summary,
                'focused_variant_id': focused_variant_id,
                'related_products':   related,
            }

            return Response(payload, status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': 'Failed to retrieve product detail', 'details': str(e)},
                status=500,
            )
 




# ──────────────────────────────────────────────────────────────
# ENQUIRY
# ──────────────────────────────────────────────────────────────

class Enquiry(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data

            name         = data.get('name', '').strip()
            organisation = data.get('organisation', '').strip()
            designation  = data.get('designation', '').strip()
            phone        = data.get('phone', '').strip()
            email        = data.get('email', '').strip()
            location     = data.get('location', '').strip()
            comment      = data.get('comment', '').strip()

            missing_fields = [
                field for field, value in {
                    'name': name, 'organisation': organisation,
                    'phone': phone, 'email': email
                }.items() if not value
            ]
            if missing_fields:
                return Response(
                    {'error': 'Missing required fields', 'missing_fields': missing_fields},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if '@' not in email:
                return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

            subject = f"New Enquiry from {name} - {organisation}"
            email_body = f"""
New Enquiry Received

Contact Information:
--------------------
Name:         {name}
Organisation: {organisation}
Designation:  {designation or 'Not provided'}
Phone:        {phone}
Email:        {email}
Location:     {location or 'Not provided'}

Message:
--------
{comment or 'No comment provided'}

---
Submitted through the ETOMOSPHERE website.
"""
            try:
                send_mail(
                    subject=subject,
                    message=email_body,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@etomosphere.local"),
                    recipient_list=[getattr(settings, "ENQUIRY_RECEIVER_EMAIL", "development@resoluteindia.co.in")],
                    fail_silently=False,
                )
                send_mail(
                    subject="Thank you for contacting ETOMOSPHERE",
                    message=f"Hello {name},\n\nThank you for reaching out. Our team will contact you soon.\n\nBest regards,\nETOMOSPHERE Team",
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@etomosphere.local"),
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"❌ Email Error: {str(e)}")

            return Response(
                {'message': 'Enquiry submitted successfully', 'status': 'success'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"❌ Error processing enquiry: {str(e)}")
            return Response(
                {'error': 'Failed to process enquiry', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )