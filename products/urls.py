from django.urls import path
from products import views



urlpatterns = [
    # Product endpoints
    path('api/products/', views.AddProduct.as_view(), name='products'),  # GET and POST
    path('api/addproduct/', views.AddProduct.as_view(), name='add-product'),  # POST only
]

