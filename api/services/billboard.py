
from api.models import Billboard
from api.serializer import BillboardSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
import base64
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter,OpenApiResponse
import uuid


class BillboardApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=BillboardSerializer,
        responses={200: BillboardSerializer, 400: BillboardSerializer.errors},
        description="Get and create billboard records",
        tags=["Billboard"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.uuid4, description="ID of the billboard record"),
        ],
    )
    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            billboards = Billboard.objects.all()
            serializer = BillboardSerializer(billboards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='supervisor').exists():
            billboards = Billboard.objects.filter(user=request.user)
            if request.query_params.get('uuid'):
                billboards = billboards.filter(uuid=request.query_params.get('uuid'))
            serializer = BillboardSerializer(billboards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)
    def post(self, request):
        if request.user.groups.filter(name='admin').exists():
            billboard = get_object_or_404(Billboard, uuid=request.data['uuid'])
            serializer = BillboardSerializer(billboard, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)
    def patch(self, request):
        if request.user.groups.filter(name='admin').exists():
            billboard = get_object_or_404(Billboard, uuid=request.data['uuid'])
            serializer = BillboardSerializer(billboard, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)
    def delete(self, request):
        if request.user.groups.filter(name='admin').exists():
            billboard = get_object_or_404(Billboard, uuid=request.data['uuid'])
            billboard.delete()
            return Response({"message": "Billboard deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)