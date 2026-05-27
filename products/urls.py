# from django.urls import path
# from products import views



# urlpatterns = [
#     # Product endpoints
#     path('api/products/', views.AddProduct.as_view(), name='products'),  # GET and POST
#     path('api/addproduct/', views.AddProduct.as_view(), name='add-product'),  # POST only
#     path('api/enquiry/', views.Enquiry.as_view(), name='enquiry'),  # POST only
# ]

from django.urls import path
from products import views

urlpatterns = [
    # Product endpoints
    # path('products/', views.AddProduct.as_view(), name='products'),       # GET and POST
    path('products/', views.ListProducts.as_view(), name='products'),   # GET
    path('addproduct/', views.AddProduct.as_view(), name='add-product'),  # POST only
    path('enquiry/', views.Enquiry.as_view(), name='enquiry'),            # POST only

    path('products/<int:product_id>/', views.ProductDetailView.as_view(), name='product-detail'),
]
