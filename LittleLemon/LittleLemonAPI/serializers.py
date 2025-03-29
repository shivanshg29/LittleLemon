from rest_framework import serializers
from .models import *

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model=MenuItem
        fields='__all__'