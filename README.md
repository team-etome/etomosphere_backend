# Etomosphere Backend

REST API backend for the Etomosphere B2B tech solutions e-commerce platform. Built with Django 5.2 and Django REST Framework.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Setup & Installation](#setup--installation)
5. [Configuration](#configuration)
6. [Data Model](#data-model)
7. [API Reference](#api-reference)
   - [Authentication](#authentication)
   - [Products](#products)
   - [Cart](#cart)
   - [Orders](#orders)
   - [Reviews](#reviews)
   - [Employees](#employees)
8. [File Storage](#file-storage)
9. [Email](#email)
10. [Apps Overview](#apps-overview)

---

## Project Overview

Etomosphere is a B2B e-commerce platform that sells tech solutions for enterprise environments — digital conference rooms, auditoriums, projector setups, and more. The backend exposes a REST API consumed by a React frontend at `etomosphere.com`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2.7 |
| API | Django REST Framework 3.16.1 |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL |
| File Storage | AWS S3 via `django-storages` + `boto3` |
| Image Processing | Pillow |
| QR Codes | `qrcode` library |
| CORS | `django-cors-headers` |

---

## Project Structure

```
etomosphere_backend/
├── backend/                  # Project config (settings, urls, storage backends)
│   ├── settings.py
│   ├── urls.py
│   ├── storage_backends.py
│   └── wsgi.py
├── accounts/                 # User authentication (register, login)
├── app1/                     # Solutions + legacy product model
├── products/                 # Hierarchical product catalog
├── cart/                     # Shopping cart
├── orders/                   # Order management
├── reviews/                  # Product reviews & ratings
├── employees/                # Employee directory with QR codes
├── manage.py
└── requirements.txt
```

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL
- AWS S3 bucket (for media storage)

### Steps

```bash
# 1. Create and activate virtual environment
python -m venv env
env\Scripts\activate          # Windows
source env/bin/activate       # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the database (see Configuration section)

# 4. Run migrations
python manage.py migrate

# 5. Create a superuser (admin)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

---

## Configuration

All config lives in `backend/settings.py`.

### Database

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'etomosphere_one',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### JWT Tokens

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

### AWS S3

```python
AWS_STORAGE_BUCKET_NAME = 'etomosphere-test-s3'
AWS_S3_REGION_NAME      = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN    = 'etomosphere-test-s3.s3.amazonaws.com'
```

S3 storage paths:

| Storage Class | S3 Prefix |
|---|---|
| `MediaStorage` | `media/` |
| `CategoryImageStorage` | `categories/` |
| `ProductImageStorage` | `products/` |

### CORS

`CORS_ALLOW_ALL_ORIGINS = True` is set in development. For production, the whitelist is:

- `https://etomosphere.com`
- `http://localhost:3000`
- `http://localhost:5173`

### Email

Gmail SMTP is used for enquiry notifications:

- **Sender:** `enquiryetomosphere@gmail.com`
- **Receiver:** `info@etome.in`

---

## Data Model

### Hierarchy

The product catalog follows a strict 4-level hierarchy:

```
Solution  (app1)
  └── Category
        └── CatalogueProduct
              └── Brand  (M2M to CatalogueProduct)
                    └── Variant  (SKU level — has price, stock, specs)
```

**Example:**

```
Solution:             Digital Conference Room
  Category:           Hardware
    CatalogueProduct: Interactive Display
      Brand:          BenQ
        Variant:      RP8603 65" — ₹1,20,000 — In Stock
        Variant:      RP7503 75" — ₹1,80,000 — In Stock
      Brand:          Samsung
        Variant:      WA65C 65"  — ₹1,50,000 — In Stock
```

### Variant Fields

| Field | Type | Notes |
|---|---|---|
| `name` | CharField | Model name, e.g. "RP8603 65 inch" |
| `sku` | CharField | Stock keeping unit |
| `mpn` | CharField | Manufacturer part number |
| `price` | DecimalField | Regular price (INR) |
| `sale_price` | DecimalField | Discounted price |
| `cost_price` | DecimalField | Internal — never exposed to frontend |
| `is_on_sale` | BooleanField | Activates sale price |
| `current_price` | property | Returns `sale_price` if on sale, else `price` |
| `discount_percentage` | property | Computed % off |
| `profit_margin` | property | Internal admin use only |
| `stock_status` | choices | `in_stock` / `out_of_stock` |
| `lifecycle_status` | choices | `active` / `discontinued` / `end_of_life` |
| `spec_json` | JSONField | Flexible specs, e.g. `{"screen_size": "65 inch", "resolution": "4K"}` |

### User Models

There are two separate user models:

| Model | Purpose | Notes |
|---|---|---|
| `God` (`accounts.God`) | Admin / staff | Set as `AUTH_USER_MODEL` — used for Django admin |
| `User` (`accounts.User`) | Customers | Used for cart, orders, reviews |

Both use `email` as the login field.

---

## API Reference

All endpoints are prefixed with `/api/`.

### Authentication

#### Register

```
POST /api/api/register/
```

**Body:**

```json
{
  "email": "user@example.com",
  "password": "secret",
  "first_name": "John",
  "phone": "9876543210"
}
```

**Response `201`:**

```json
{
  "detail": "Account created successfully.",
  "user": { "id": 1, "email": "user@example.com", "first_name": "John", "phone": "9876543210" },
  "tokens": { "access": "<jwt>", "refresh": "<jwt>" }
}
```

#### Login

```
POST /api/api/login/
```

**Body:**

```json
{
  "email": "user@example.com",
  "password": "secret"
}
```

**Response `200`:**

```json
{
  "message": "Login successful.",
  "user": { "id": 1, "email": "user@example.com", "first_name": "John", "phone": "" },
  "tokens": { "access": "<jwt>", "refresh": "<jwt>" }
}
```

**Errors:** `400` missing fields · `401` invalid credentials · `403` inactive account

> All authenticated endpoints require the header:
> `Authorization: Bearer <access_token>`

---

### Products

#### List All Products

```
GET /api/products/
```

No authentication required. Returns the full catalog tree.

**Response `200`:**

```json
{
  "count": 2,
  "categories": [
    {
      "id": 1,
      "name": "Hardware",
      "slug": "hardware",
      "solution": "Digital Conference Room",
      "images": [{ "image_url": "...", "is_main": true }],
      "products": [
        {
          "id": 1,
          "name": "Interactive Display",
          "slug": "interactive-display",
          "description": "...",
          "images": [],
          "brands": [
            {
              "id": 1,
              "name": "BenQ",
              "website": "https://benq.com",
              "variants": [
                {
                  "id": 1,
                  "name": "RP8603 65 inch",
                  "sku": "RP8603",
                  "price": "120000.00",
                  "sale_price": null,
                  "current_price": "120000.00",
                  "currency": "INR",
                  "is_on_sale": false,
                  "discount_percentage": 0,
                  "stock_status": "in_stock",
                  "lifecycle_status": "active",
                  "spec_json": { "screen_size": "65 inch", "resolution": "4K" },
                  "images": []
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

#### Product Detail

```
GET /api/products/<id>/
GET /api/products/<id>/?type=variant
GET /api/products/<id>/?type=product   (default)
```

No authentication required.

- `type=product` — `id` is a `CatalogueProduct` primary key
- `type=variant` — `id` is a `Variant` primary key; the response marks that variant as `is_focused: true`

**Response `200`:**

```json
{
  "id": 1,
  "name": "Interactive Display",
  "slug": "interactive-display",
  "description": "...",
  "category": {
    "id": 1,
    "name": "Hardware",
    "slug": "hardware",
    "solution_name": "Digital Conference Room",
    "solution_slug": "digital-conference-room"
  },
  "images": [],
  "brands": [],
  "price_summary": { "min": 120000.0, "max": 180000.0, "currency": "INR" },
  "focused_variant_id": null,
  "related_products": [
    { "id": 2, "name": "PTZ Camera", "slug": "ptz-camera", "image": "..." }
  ]
}
```

#### Add Product (Admin)

```
POST /api/addproduct/
Content-Type: multipart/form-data
```

Creates a full product entry across all 4 hierarchy levels in a single atomic transaction. Uses `get_or_create` for Category, CatalogueProduct, and Brand — only Variant is always created new.

**Required fields:**

| Field | Description |
|---|---|
| `category_slug` | Unique slug for the category, e.g. `hardware` |
| `category_name` | Display name, e.g. `Hardware` |
| `product_name` | e.g. `Interactive Display` |
| `product_slug` | Unique slug, e.g. `interactive-display` |
| `brand_name` | e.g. `BenQ` |
| `variant_name` | e.g. `RP8603 65 inch` |
| `price` | Numeric price value |

**Optional fields:**

| Field | Default | Description |
|---|---|---|
| `category_description` | `""` | Category description |
| `product_description` | `""` | Product description |
| `variant_description` | `""` | Variant description |
| `brand_website` | `""` | Brand URL |
| `sku` | `""` | Stock keeping unit |
| `mpn` | `""` | Manufacturer part number |
| `sale_price` | `null` | Discounted price |
| `cost_price` | `null` | Internal cost (not exposed to frontend) |
| `currency` | `INR` | 3-letter currency code |
| `is_on_sale` | `false` | `true` / `false` / `1` / `0` |
| `stock_status` | `in_stock` | `in_stock` or `out_of_stock` |
| `lifecycle_status` | `active` | `active`, `discontinued`, or `end_of_life` |
| `spec_json` | `{}` | JSON string of product specs |
| `category_image` | — | Single image file |
| `product_images[]` | — | Multiple image files |
| `variant_images[]` | — | Multiple image files |
| `product_image_main_0` | `false` | Mark first product image as main |
| `variant_image_main_0` | `false` | Mark first variant image as main |

Image constraints: JPEG, PNG, WebP, or GIF · max 30 MB per file

**Response `201`:**

```json
{ "message": "Product created successfully" }
```

#### Enquiry / Contact Form

```
POST /api/enquiry/
```

No authentication required. Sends an email to `info@etome.in` and a confirmation to the submitter.

**Body:**

```json
{
  "name": "John Doe",
  "organisation": "ACME Corp",
  "designation": "IT Manager",
  "phone": "9876543210",
  "email": "john@acme.com",
  "location": "Mumbai",
  "comment": "We need a conference room solution."
}
```

Required: `name`, `organisation`, `phone`, `email`.

**Response `200`:**

```json
{ "message": "Enquiry submitted successfully", "status": "success" }
```

---

### Cart

Authentication required for all cart endpoints.

#### Add to Cart

```
POST /api/api/addCart/
```

```json
{ "variant_id": 1, "quantity": 2 }
```

#### Remove Item

```
DELETE /api/api/remove/
```

```json
{ "item_id": 5 }
```

#### Update Quantity

```
PUT /api/api/update/
```

```json
{ "item_id": 5, "quantity": 3 }
```

#### Clear Cart

```
DELETE /api/api/clear/
```

#### ViewSet (RESTful)

```
GET  /api/cart/       List carts
GET  /api/cart/<id>/  Cart detail
```

**Cart response includes:**

```json
{
  "id": 1,
  "total_items": 3,
  "total_price": "360000.00",
  "items": [
    {
      "id": 1,
      "product": { "id": 1, "name": "RP8603 65 inch" },
      "quantity": 2,
      "total_price": "240000.00"
    }
  ]
}
```

---

### Orders

Authentication required for all order endpoints.

#### List Orders

```
GET /api/api/
```

Returns all orders for the authenticated user.

#### Order Detail

```
GET /api/api/<id>/
```

#### Create Order

```
POST /api/api/create/
```

Creates an order from the user's current cart.

```json
{
  "shipping_address": "123 Main St, Mumbai 400001",
  "billing_address": "123 Main St, Mumbai 400001",
  "phone": "9876543210"
}
```

**Order statuses:** `pending` → `confirmed` → `processing` → `shipped` → `delivered` / `cancelled`

**Payment statuses:** `pending` → `paid` / `failed` / `refunded`

#### Update Order Status (Admin)

```
PUT /api/api/<id>/update-status/
```

```json
{ "status": "confirmed" }
```

#### ViewSet (RESTful)

```
GET  /api/orders/
GET  /api/orders/<id>/
```

---

### Reviews

#### List Reviews for a Product

```
GET /api/api/products/<product_pk>/reviews/
```

No authentication required. `product_pk` is a `Variant` ID.

#### My Reviews

```
GET /api/api/my-reviews/
```

Authentication required. Returns all reviews by the current user.

#### Review Detail

```
GET /api/api/reviews/<id>/
```

#### Create Review

```
POST /api/api/products/<product_pk>/reviews/
```

Authentication required.

```json
{
  "rating": 5,
  "title": "Excellent display",
  "comment": "Crystal clear image quality, easy installation."
}
```

Rating must be between 1 and 5.

---

### Employees

#### Employee Profile

```
GET /api/employees/<slug>/
```

No authentication required. Returns public employee profile data.

**Response `200`:**

```json
{
  "name": "John Doe",
  "designation": "Solutions Architect",
  "phone": "+91 98765 43210",
  "email": "john@etomosphere.com",
  "region": "Mumbai",
  "photo": "https://etomosphere-test-s3.s3.amazonaws.com/logos/photo.jpg",
  "qr_code": "https://etomosphere-test-s3.s3.amazonaws.com/logos/abc123_qr.png"
}
```

The QR code encodes the URL `https://etomosphere.com/employee/<slug>`. Slug is a UUID hex string generated once on first save and never changed.

---

## File Storage

S3 is the only media storage backend. Static files (Django admin) are served locally.

| Type | S3 Path | Storage Class |
|---|---|---|
| Category images | `categories/` | `CategoryImageStorage` |
| Product & variant images | `products/` | `ProductImageStorage` |
| Employee photos & QR codes | `logos/` | `S3Boto3Storage` |
| General media | `media/` | `MediaStorage` |

CDN domain: `etomosphere-test-s3.s3.amazonaws.com`

Cache-Control is set to `max-age=86400` (24 hours) on all S3 objects.

---

## Email

Two emails are sent per enquiry submission:

1. **Internal notification** → `info@etome.in` — full contact details and message body
2. **Confirmation** → submitter's email — acknowledgement that the team will follow up

Configured in `settings.py` using Gmail SMTP (`smtp.gmail.com`, port 587, TLS).

---

## Apps Overview

| App | Description |
|---|---|
| `backend` | Project settings, root URL config, S3 storage backends |
| `accounts` | Custom user models (`God`, `User`), register and login views |
| `app1` | `Solution` model (top of hierarchy) + legacy flat `Product` model (deprecated) |
| `products` | Full hierarchical catalog: `Category`, `CatalogueProduct`, `Brand`, `Variant` + image models |
| `cart` | `Cart` and `CartItem` models; add/remove/update/clear endpoints |
| `orders` | `Order` and `OrderItem` models; full order lifecycle management |
| `reviews` | `ProductReview` model; per-variant star ratings and comments |
| `employees` | `Employee` model with auto-generated UUID slug and S3-hosted QR codes |

> **Note:** `app1.Product` is a legacy flat product model kept for backwards compatibility. All new product data uses the hierarchical structure in the `products` app. Do not remove `app1.Product` until all usages are migrated.
