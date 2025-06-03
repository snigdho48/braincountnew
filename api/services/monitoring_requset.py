from api.models import TaskSubmissionRequest, Notification
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
from api.serializer import TaskSubmissionSerializer,TaskSubmissionRequestSerializer
from api.services.constants import TASK_CHOICES
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class MonitoringRequestApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=TaskSubmissionRequestSerializer,
        responses={200: TaskSubmissionRequestSerializer, 400: TaskSubmissionRequestSerializer.errors},
        description="Get and create monitoring records",
        tags=["TaskSubmission"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.UUID, description="ID of the monitoring record"),
            OpenApiParameter(name='status', type=str, description="Status of the monitoring record"),
        ],
    )
    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = TaskSubmissionRequest.objects.all()
            pending = TaskSubmissionRequest.objects.filter(is_accepted='PENDING').count()
            accepted = TaskSubmissionRequest.objects.filter(is_accepted='ACCEPTED').count()
            all_task = monitoring.count()

            if request.query_params.get('uuid'):
                monitoring = monitoring.filter(uuid=request.query_params.get('uuid'))
            if request.query_params.get('status'):
                monitoring = monitoring.filter(is_accepted=request.query_params.get('status'))
            if request.query_params.get('exclude'):
                monitoring = monitoring.exclude(is_accepted=request.query_params.get('exclude'))

            serializer = TaskSubmissionRequestSerializer(monitoring, many=True)
            serializer_data = {
                "monitoring": serializer.data,
                "pending": pending,
                "accepted": accepted,
                "all_task": all_task
            }
            return Response(serializer_data, status=status.HTTP_200_OK)

        elif request.user.groups.filter(name='supervisor').exists():
            monitoring = TaskSubmissionRequest.objects.filter(user=request.user)
            pending = monitoring.filter(is_accepted='PENDING').count()
            accepted = monitoring.filter(is_accepted='ACCEPTED').count()
            completed = monitoring.filter(is_accepted='COMPLETED').count()
            all_task = monitoring.count()

            if request.query_params.get('uuid'):
                monitoring = monitoring.filter(uuid=request.query_params.get('uuid'))
            if request.query_params.get('status'):
                monitoring = monitoring.filter(is_accepted=request.query_params.get('status'))
            if request.query_params.get('exclude'):
                monitoring = monitoring.exclude(is_accepted=request.query_params.get('exclude'))
            serializer = TaskSubmissionRequestSerializer(monitoring, many=True)
            serializer_data = {
                "monitoring": serializer.data,
                "pending": pending,
                "accepted": accepted,
                'completed': completed,
                "all_task": all_task
            }
            
            return Response(serializer_data, status=status.HTTP_200_OK)

        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)

    @extend_schema(
        request=TaskSubmissionRequestSerializer,
        responses={200: TaskSubmissionRequestSerializer, 400: TaskSubmissionRequestSerializer.errors},
        description="Create a new monitoring record",
        tags=["TaskSubmission"],
    )
    def post(self, request):
        serializer = TaskSubmissionRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        request=TaskSubmissionRequestSerializer,
        responses={200: TaskSubmissionRequestSerializer, 400: TaskSubmissionRequestSerializer.errors},
        description="Update a monitoring record",
        tags=["TaskSubmission"],
    )
    def patch(self, request):
        if request.user.groups.filter(name__in=['admin', 'supervisor']).exists():
            monitoring = get_object_or_404(TaskSubmissionRequest, uuid=request.data['uuid'])
            # Save old status for notification
            old_status = monitoring.is_accepted
            serializer = TaskSubmissionRequestSerializer(monitoring, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # Send notification if status changed
                new_status = serializer.instance.is_accepted
                if old_status != new_status:
                    notif = Notification.objects.create(
                        user=serializer.instance.user,
                        message=f"Your task request status changed from {old_status} to {new_status}.",
                        type='task_request'
                    )
                    self.send_realtime_notification(serializer.instance.user.id, {
                        "message": notif.message,
                        "type": notif.type,
                        "created_at": str(notif.created_at),
                        "is_read": notif.is_read,
                    })
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)

    def send_realtime_notification(self, user_id, content):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_notification",
                "content": content,
            }
        )
        
    @extend_schema(
        request=TaskSubmissionRequestSerializer,
        responses={200: OpenApiResponse(description="TaskSubmission record deleted")},
        description="Delete a monitoring record",
        tags=["TaskSubmission"],
    )
    def delete(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = get_object_or_404(TaskSubmissionRequest, uuid=request.data['uuid'])
            monitoring.delete()
            return Response({"message": "TaskSubmission record deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)
        
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