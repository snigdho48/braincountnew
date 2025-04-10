
from api.models import MonitoringRequest
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
import base64
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter,OpenApiResponse
import uuid
from api.serializer import MonitoringRequestSerializer


class MonitoringRequestApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=MonitoringRequestSerializer,
        responses={200: MonitoringRequestSerializer, 400: MonitoringRequestSerializer.errors},
        description="Get and create monitoring records",
        tags=["Monitoring"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.uuid4, description="ID of the monitoring record"),
        ],
    )
    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = MonitoringRequest.objects.all()
            if request.query_params.get('uuid'):
                monitoring = monitoring.filter(uuid=request.query_params.get('uuid'))
            serializer = MonitoringRequestSerializer(monitoring, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='supervisor').exists():
            monitoring = MonitoringRequest.objects.filter(user=request.user)
            if request.query_params.get('uuid'):
                monitoring = monitoring.filter(uuid=request.query_params.get('uuid'))
            serializer = MonitoringRequestSerializer(monitoring, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)
    def post(self, request):
        serializer = MonitoringRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = get_object_or_404(MonitoringRequest, uuid=request.data['uuid'])
            serializer = MonitoringRequestSerializer(monitoring, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)
    def delete(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = get_object_or_404(MonitoringRequest, uuid=request.data['uuid'])
            monitoring.delete()
            return Response({"message": "Monitoring record deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)