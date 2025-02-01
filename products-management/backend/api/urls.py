from django.urls import path
from .views import CategoryListCreate, CategoryDetail, ProductListCreate, ProductDetail, get_category_by_name_or_id, search_product_by_image

urlpatterns = [
    path('categories/', CategoryListCreate.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('category/', get_category_by_name_or_id, name='category-search'),
    path('products/', ProductListCreate.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('products/search-by-image/', search_product_by_image, name='search-product-image'),
]
