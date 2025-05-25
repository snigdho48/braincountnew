from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404
import uuid

from api.models import Poi
from api.serializer import PoiSerializer

class PoiApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PoiSerializer,
        responses={200: PoiSerializer, 400: PoiSerializer.errors},
        description="Get and create Poi records",
        tags=["Poi"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.UUID, description="UUID of the Poi", required=False),
        ],
    )
    def get(self, request):
        pois = Poi.objects.all()
        if request.query_params.get('uuid'):
            pois = pois.filter(uuid=request.query_params.get('uuid'))
        serializer = PoiSerializer(pois, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PoiSerializer,
        responses={200: PoiSerializer, 400: PoiSerializer.errors},
        description="Create a new Poi record",
        tags=["Poi"],
    )
    def post(self, request):
        serializer = PoiSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=PoiSerializer,
        responses={200: PoiSerializer, 400: PoiSerializer.errors},
        description="Update a Poi record",
        tags=["Poi"],
    )
    def patch(self, request):
        poi = get_object_or_404(Poi, uuid=request.data['uuid'])
        serializer = PoiSerializer(poi, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
