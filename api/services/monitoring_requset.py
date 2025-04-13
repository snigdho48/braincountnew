
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
from api.services.constants import TASK_CHOICES


class MonitoringRequestApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=MonitoringRequestSerializer,
        responses={200: MonitoringRequestSerializer, 400: MonitoringRequestSerializer.errors},
        description="Get and create monitoring records",
        tags=["Monitoring"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.UUID, description="ID of the monitoring record"),
            OpenApiParameter(name='status', type=str, description="Status of the monitoring record"),
        ],
    )
    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = MonitoringRequest.objects.all()
            pending = MonitoringRequest.objects.filter(is_accepeted='PENDING').count()
            accepted = MonitoringRequest.objects.filter(is_accepeted='ACCEPTED').count()
            all_task = monitoring.count()

            if request.query_params.get('uuid'):
                monitoring = monitoring.filter(uuid=request.query_params.get('uuid'))
            if request.query_params.get('status'):
                monitoring = monitoring.filter(is_accepeted=request.query_params.get('status'))

            serializer = MonitoringRequestSerializer(monitoring, many=True)
            serializer_data = {
                "monitoring": serializer.data,
                "pending": pending,
                "accepted": accepted,
                "all_task": all_task
            }
            return Response(serializer_data, status=status.HTTP_200_OK)

        elif request.user.groups.filter(name='supervisor').exists():
            monitoring = MonitoringRequest.objects.filter(user=request.user)
            pending = monitoring.filter(is_accepeted='PENDING').count()
            accepted = monitoring.filter(is_accepeted='ACCEPTED').count()
            all_task = monitoring.count()

            if request.query_params.get('uuid'):
                monitoring = monitoring.filter(uuid=request.query_params.get('uuid'))
            if request.query_params.get('status'):
                monitoring = monitoring.filter(is_accepeted=request.query_params.get('status'))

            serializer = MonitoringRequestSerializer(monitoring, many=True)
            serializer_data = {
                "monitoring": serializer.data,
                "pending": pending,
                "accepted": accepted,
                "all_task": all_task
            }
            return Response(serializer_data, status=status.HTTP_200_OK)

        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        request=MonitoringRequestSerializer,
        responses={200: MonitoringRequestSerializer, 400: MonitoringRequestSerializer.errors},
        description="Create a new monitoring record",
        tags=["Monitoring"],
    )
    def post(self, request):
        serializer = MonitoringRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        request=MonitoringRequestSerializer,
        responses={200: MonitoringRequestSerializer, 400: MonitoringRequestSerializer.errors},
        description="Update a monitoring record",
        tags=["Monitoring"],
    )
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
    @extend_schema(
        request=MonitoringRequestSerializer,
        responses={200: OpenApiResponse(description="Monitoring record deleted")},
        description="Delete a monitoring record",
        tags=["Monitoring"],
    )
    def delete(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = get_object_or_404(MonitoringRequest, uuid=request.data['uuid'])
            monitoring.delete()
            return Response({"message": "Monitoring record deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_403_FORBIDDEN)
        
class MonitoringRequestStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
  
    @extend_schema(
        request=None,
        description="Get Task Choices status",
        tags=["Billboard"],
        responses={
            200: OpenApiResponse(
                description="Task Choices status",
                examples=[
                    {
                        "name": "Success",
                        "value": {
                "status": [statustuple[0] for statustuple in TASK_CHOICES]
                        }
                    }
                ]
            )
        }
    )
    def get(self, request):
        return Response(
            {
                "status": [statustuple[0] for statustuple in TASK_CHOICES]
            },
            status=status.HTTP_200_OK
        )