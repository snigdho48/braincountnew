from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from api.models import Billboard_info
from api.serializer import Billboard_infoSerializer

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
