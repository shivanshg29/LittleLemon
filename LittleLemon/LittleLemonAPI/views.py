from django.shortcuts import render,HttpResponse
from rest_framework import status,permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

# Create your views here.
@api_view(['GET','POST'])
@permission_classes([permissions.IsAuthenticated])
def MenuItems(request):
    if request.method=='GET':
        menu_items=MenuItem.objects.all()
        serializer=MenuSerializer(menu_items,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    if request.method=='POST':
        if not request.user.groups.filter(name="Manager").exists():
            return Response({'detail':'Unauthorized User'},status=status.HTTP_403_FORBIDDEN)
        
        serializer=MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response({'detail':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([permissions.IsAuthenticated])
def MenuItemDetail(request,pk):
    menu_item=get_object_or_404(MenuItem, pk=pk)
    if request.method=='GET':
        serializer=MenuSerializer(menu_item)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    if not request.user.groups.filter(name="Manager").exists():
            return Response({'detail':'Unauthorized User'},status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        serializer = MenuSerializer(menu_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        menu_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)