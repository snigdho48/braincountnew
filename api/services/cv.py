from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from api.models import Cv, Billboard_View, Billboard
from api.serializer import CvSerializer

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
        data = request.data
        view = get_object_or_404(Billboard_View, camera_id=data['camera_id'])
        billboard = get_object_or_404(Billboard, view=view.id)
        data['billboard'] = billboard.id
        data['view'] = view.id
        serializer = CvSerializer(data=request.data,many=True)
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
