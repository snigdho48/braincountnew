from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404
import uuid

from api.models import Location
from api.serializer import LocationSerializer

class LocationApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LocationSerializer,
        responses={200: LocationSerializer, 400: LocationSerializer.errors},
        description="Get and create Location records",
        tags=["Location"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.UUID, description="UUID of the Location", required=False),
        ],
    )
    def get(self, request):
        locations = Location.objects.all()
        if request.query_params.get('uuid'):
            locations = locations.filter(uuid=request.query_params.get('uuid'))
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=LocationSerializer,
        responses={200: LocationSerializer, 400: LocationSerializer.errors},
        description="Create a new Location record",
        tags=["Location"],
    )
    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=LocationSerializer,
        responses={200: LocationSerializer, 400: LocationSerializer.errors},
        description="Update a Location record",
        tags=["Location"],
    )
    def patch(self, request):
        location = get_object_or_404(Location, uuid=request.data['uuid'])
        serializer = LocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
