from rest_framework import generics, filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import CategoryTB, ProductTB
from .serializers import CategorySerializer, ProductSerializer, ImageUploadSerializer
from rest_framework.decorators import api_view, parser_classes
from django.conf import settings
import cv2
import numpy as np
import os
from rest_framework.parsers import MultiPartParser, FormParser
from .forms import ImageUploadForm

# CRUD for Category
class CategoryListCreate(generics.ListCreateAPIView):
    queryset = CategoryTB.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CategoryTB.objects.all()
    serializer_class = CategorySerializer

@api_view(['GET'])
def get_category_by_name_or_id(request):
    category_id = request.GET.get('id')
    category_name = request.GET.get('name')
    
    if category_id:
        category = get_object_or_404(CategoryTB, id=category_id)
    elif category_name:
        category = get_object_or_404(CategoryTB, name=category_name)
    else:
        return Response({"error": "Provide id or name"}, status=400)

    serializer = CategorySerializer(category)
    return Response(serializer.data)

# CRUD for Product
class ProductListCreate(generics.ListCreateAPIView):
    queryset = ProductTB.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'name']

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductTB.objects.all()
    serializer_class = ProductSerializer

@api_view(['POST'])
# @parser_classes([MultiPartParser])
@parser_classes([MultiPartParser, FormParser])
def search_product_by_image(request):
    """
    Accepts an image upload, searches for similar products, 
    and returns the top 10 most similar products.
    """

    # form = ImageUploadForm(request.POST, request.FILES)
    # if form.is_valid():
    #     # Save the uploaded image temporarily

    serializer = ImageUploadSerializer(data=request.data)  
    if not serializer.is_valid():
        return Response({"error": "Invalid file"}, status=400)

    if 'image' not in request.FILES:
        return Response({"error": "No image uploaded"}, status=400)

    uploaded_image = request.FILES['image']

    temp_image_path = os.path.join(settings.MEDIA_ROOT, 'temp_uploaded.jpg')

    # Save uploaded image temporarily
    with open(temp_image_path, 'wb') as f:
        for chunk in uploaded_image.chunks():
            f.write(chunk)

    # Load and process the uploaded image
    query_img = cv2.imread(temp_image_path, cv2.IMREAD_GRAYSCALE)
    if query_img is None:
        return Response({"error": "Invalid image format"}, status=400)

    sift = cv2.SIFT_create()
    query_kp, query_des = sift.detectAndCompute(query_img, None)

    if query_des is None:
        return Response({"error": "Couldn't extract features from image"}, status=400)

    # Store similarity scores
    similarity_scores = []

    for product in ProductTB.objects.all():
        product_img_path = os.path.join(settings.MEDIA_ROOT, str(product.image))

        if not os.path.exists(product_img_path):
            continue

        # Load product image
        product_img = cv2.imread(product_img_path, cv2.IMREAD_GRAYSCALE)
        if product_img is None:
            continue

        product_kp, product_des = sift.detectAndCompute(product_img, None)
        if product_des is None:
            continue

        # Feature matching
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(query_des, product_des, k=2)

        # Apply ratio test
        good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

        similarity_scores.append((len(good_matches), product))

    # Sort products by similarity
    similarity_scores.sort(reverse=True, key=lambda x: x[0])
    top_products = [product for _, product in similarity_scores[:2]]

    # Serialize and return response
    serializer = ProductSerializer(top_products, many=True)
    return Response(serializer.data)
