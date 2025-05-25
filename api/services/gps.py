from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from api.models import Gps
from api.serializer import GpsSerializer

class GpsApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=GpsSerializer,
        responses={200: GpsSerializer, 400: GpsSerializer.errors},
        description="Get and create Gps records",
        tags=["Gps"],
        parameters=[
            OpenApiParameter(name='id', type=int, description="ID of the Gps", required=False),
        ],
    )
    def get(self, request):
        gps = Gps.objects.all()
        if request.query_params.get('id'):
            gps = gps.filter(id=request.query_params.get('id'))
        serializer = GpsSerializer(gps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=GpsSerializer,
        responses={200: GpsSerializer, 400: GpsSerializer.errors},
        description="Create a new Gps record",
        tags=["Gps"],
    )
    def post(self, request):
        data = request.data
        serializer = GpsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=GpsSerializer,
        responses={200: GpsSerializer, 400: GpsSerializer.errors},
        description="Update a Gps record",
        tags=["Gps"],
    )
    def patch(self, request):
        gps = get_object_or_404(Gps, id=request.data['id'])
        serializer = GpsSerializer(gps, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
