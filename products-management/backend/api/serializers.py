from rest_framework import serializers
from .models import CategoryTB, ProductTB

class CategorySerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = CategoryTB
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTB
        fields = '__all__'

class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
