from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404
import uuid

from api.models import Location, Billboard_info, Poi, Cv_count, Gps, Cv
from api.serializer import (
    LocationSerializer, Billboard_infoSerializer, PoiSerializer,
    Cv_countSerializer, GpsSerializer, CvSerializer
)

# Helper function for GET, POST, PATCH

def get_object_by_uuid(model, uuid_value):
    return get_object_or_404(model, uuid=uuid_value)

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

class BillboardInfoApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=Billboard_infoSerializer,
        responses={200: Billboard_infoSerializer, 400: Billboard_infoSerializer.errors},
        description="Get and create Billboard_info records",
        tags=["Billboard_info"],
        parameters=[
            OpenApiParameter(name='id', type=int, description="ID of the Billboard_info", required=False),
        ],
    )
    def get(self, request):
        infos = Billboard_info.objects.all()
        if request.query_params.get('id'):
            infos = infos.filter(id=request.query_params.get('id'))
        serializer = Billboard_infoSerializer(infos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=Billboard_infoSerializer,
        responses={200: Billboard_infoSerializer, 400: Billboard_infoSerializer.errors},
        description="Create a new Billboard_info record",
        tags=["Billboard_info"],
    )
    def post(self, request):
        serializer = Billboard_infoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=Billboard_infoSerializer,
        responses={200: Billboard_infoSerializer, 400: Billboard_infoSerializer.errors},
        description="Update a Billboard_info record",
        tags=["Billboard_info"],
    )
    def patch(self, request):
        info = get_object_or_404(Billboard_info, id=request.data['id'])
        serializer = Billboard_infoSerializer(info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class CvCountApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=Cv_countSerializer,
        responses={200: Cv_countSerializer, 400: Cv_countSerializer.errors},
        description="Get and create Cv_count records",
        tags=["Cv_count"],
        parameters=[
            OpenApiParameter(name='id', type=int, description="ID of the Cv_count", required=False),
        ],
    )
    def get(self, request):
        counts = Cv_count.objects.all()
        if request.query_params.get('id'):
            counts = counts.filter(id=request.query_params.get('id'))
        serializer = Cv_countSerializer(counts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=Cv_countSerializer,
        responses={200: Cv_countSerializer, 400: Cv_countSerializer.errors},
        description="Create a new Cv_count record",
        tags=["Cv_count"],
    )
    def post(self, request):
        serializer = Cv_countSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=Cv_countSerializer,
        responses={200: Cv_countSerializer, 400: Cv_countSerializer.errors},
        description="Update a Cv_count record",
        tags=["Cv_count"],
    )
    def patch(self, request):
        count = get_object_or_404(Cv_count, id=request.data['id'])
        serializer = Cv_countSerializer(count, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class CvApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CvSerializer,
        responses={200: CvSerializer, 400: CvSerializer.errors},
        description="Get and create Cv records",
        tags=["Cv"],
        parameters=[
            OpenApiParameter(name='id', type=int, description="ID of the Cv", required=False),
        ],
    )
    def get(self, request):
        cvs = Cv.objects.all()
        if request.query_params.get('id'):
            cvs = cvs.filter(id=request.query_params.get('id'))
        serializer = CvSerializer(cvs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CvSerializer,
        responses={200: CvSerializer, 400: CvSerializer.errors},
        description="Create a new Cv record",
        tags=["Cv"],
    )
    def post(self, request):
        serializer = CvSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CvSerializer,
        responses={200: CvSerializer, 400: CvSerializer.errors},
        description="Update a Cv record",
        tags=["Cv"],
    )
    def patch(self, request):
        cv = get_object_or_404(Cv, id=request.data['id'])
        serializer = CvSerializer(cv, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
