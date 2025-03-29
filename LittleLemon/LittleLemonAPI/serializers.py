from rest_framework import serializers
from .models import *

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model=MenuItem
        fields='__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields='__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields='__all__'