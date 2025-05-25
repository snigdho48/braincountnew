from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from api.models import Cv_count
from api.serializer import Cv_countSerializer

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
