# Django Backend Project

This is a Django backend project set up with all necessary components for frontend connectivity.

## Project Structure

- **Project Name**: backend
- **App Name**: app1
- **Database**: SQLite (default)

## Installed Packages

- Django 5.2.7
- Django REST Framework 3.16.1
- Django CORS Headers 4.9.0

## Setup Instructions

1. **Activate Virtual Environment**:
   ```bash
   venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Core Endpoints
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Test API**: http://127.0.0.1:8000/api/test/
- **API Root**: http://127.0.0.1:8000/api/

### Accounts API (`/api/accounts/`)
- `POST /register/` - User registration
- `POST /login/` - User login
- `POST /logout/` - User logout
- `GET /profile/` - Get user profile
- `PUT /profile/` - Update user profile
- `GET /users/` - List users (authenticated)
- `GET /users/{id}/` - User details (authenticated)

### Products API (`/api/products/`)
- `GET /categories/` - List product categories
- `GET /categories/{id}/` - Category details
- `GET /products/` - List products (with filtering & search)
- `GET /products/{id}/` - Product details
- `GET /products/featured/` - Featured products
- `GET /products/on-sale/` - Products on sale
- `GET /products/search/?q=query` - Search products

### Cart API (`/api/cart/`)
- `GET /` - Get user's cart
- `POST /add/` - Add item to cart
- `DELETE /remove/` - Remove item from cart
- `PUT /update/` - Update item quantity
- `DELETE /clear/` - Clear all cart items

### Orders API (`/api/orders/`)
- `GET /` - List user's orders
- `GET /{id}/` - Order details
- `POST /create/` - Create order from cart
- `PUT /{id}/update-status/` - Update order status

### Reviews API (`/api/reviews/`)
- `GET /products/{id}/reviews/` - List product reviews
- `POST /products/{id}/reviews/` - Create product review
- `GET /reviews/{id}/` - Review details
- `PUT /reviews/{id}/` - Update review
- `DELETE /reviews/{id}/` - Delete review
- `GET /my-reviews/` - List user's reviews

## Frontend Connectivity

The backend is configured with:
- **CORS enabled** for cross-origin requests
- **REST Framework** for API endpoints
- **Allowed origins**: localhost:3000, localhost:3001, 127.0.0.1:3000, 127.0.0.1:3001

## Development Notes

- Debug mode is enabled for development
- CORS allows all origins (development only)
- REST Framework uses JSON renderer and parser by default
- Authentication is set to AllowAny (can be changed for production)

## Next Steps

1. Add your models in `app1/models.py`
2. Create serializers in `app1/serializers.py`
3. Add viewsets in `app1/views.py`
4. Update URL patterns in `app1/urls.py`
# Auto-deploy test
