from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from api.models import Billboard_View
from api.serializer import Billboard_ViewSerializer

class BillboardViewApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=Billboard_ViewSerializer,
        responses={200: Billboard_ViewSerializer, 400: Billboard_ViewSerializer.errors},
        description="Get and create Billboard_View records",
        tags=["Billboard_View"],
        parameters=[
            OpenApiParameter(name='id', type=int, description="ID of the Billboard_View", required=False),
        ],
    )
    def get(self, request):
        views = Billboard_View.objects.all()
        if request.query_params.get('id'):
            views = views.filter(id=request.query_params.get('id'))
        serializer = Billboard_ViewSerializer(views, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=Billboard_ViewSerializer,
        responses={200: Billboard_ViewSerializer, 400: Billboard_ViewSerializer.errors},
        description="Create a new Billboard_View record",
        tags=["Billboard_View"],
    )
    def post(self, request):
        serializer = Billboard_ViewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=Billboard_ViewSerializer,
        responses={200: Billboard_ViewSerializer, 400: Billboard_ViewSerializer.errors},
        description="Update a Billboard_View record",
        tags=["Billboard_View"],
    )
    def patch(self, request):
        view = get_object_or_404(Billboard_View, id=request.data['id'])
        serializer = Billboard_ViewSerializer(view, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
