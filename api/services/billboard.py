
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
            OpenApiParameter(name='uuid', type=uuid.UUID, description="UUID of the billboard", required=False),
        ],
       
    )
    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            billboards = Billboard.objects.all()
            serializer = BillboardSerializer(billboards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='supervisor').exists():
            billboards = Billboard.objects.all()
            if request.query_params.get('uuid'):
                billboards = billboards.filter(uuid=request.query_params.get('uuid'))
            serializer = BillboardSerializer(billboards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)
    @extend_schema(
        request=BillboardSerializer,
        responses={200: BillboardSerializer, 400: BillboardSerializer.errors},
        description="Create a new billboard record",
        tags=["Billboard"],
    )
    def post(self, request):
        if request.user.groups.filter(name='admin').exists():
            billboard = get_object_or_404(Billboard, uuid=request.data['uuid'])
            serializer = BillboardSerializer(billboard, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)
    @extend_schema(
        request=BillboardSerializer,
        responses={200: BillboardSerializer, 400: BillboardSerializer.errors},
        description="Update a billboard record",
        tags=["Billboard"],
    )
    def patch(self, request):
        if request.user.groups.filter(name='admin').exists():
            billboard = get_object_or_404(Billboard, uuid=request.data['uuid'])
            serializer = BillboardSerializer(billboard, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='uuid',
                type=uuid.UUID,
                location=OpenApiParameter.QUERY,
                description="UUID of the billboard",
                required=True,
            )
        ],
        responses={200: BillboardSerializer, 403: None, 404: None},
        description="Delete a billboard record",
        tags=["Billboard"],
    )
    def delete(self, request):
        if request.user.groups.filter(name='admin').exists():
            uuid_param = request.query_params.get('uuid')
            if not uuid_param:
                return Response({"message": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                billboard_uuid = uuid.UUID(uuid_param)
            except ValueError:
                return Response({"message": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)

            billboard = get_object_or_404(Billboard, uuid=billboard_uuid)
            billboard.delete()
            return Response({"message": "Billboard deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You are not authorized to delete this data"}, status=status.HTTP_401_UNAUTHORIZED)