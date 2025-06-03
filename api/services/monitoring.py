from api.models import TaskSubmission,BILLBOARD_STATUS,TaskSubmissionRequest, Notification
from api.serializer import TaskSubmissionSerializer,TaskReSubmissionSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
import base64
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter,OpenApiResponse
import uuid
from rest_framework.parsers import MultiPartParser, FormParser
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer






class BillboardStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        description="Get billboard status",
        tags=["Billboard"],
        responses={
            200: OpenApiResponse(
                description="Billboard status",
                examples=[
                    {
                        "name": "Success",
                        "value": {
                "status": [statustuple[0] for statustuple in BILLBOARD_STATUS]
                        }
                    }
                ]
            )
        }
    )
    def get(self, request):
        return Response(
            {
                "status": [statustuple[0] for statustuple in BILLBOARD_STATUS]
            },
            status=status.HTTP_200_OK
        )
    
class MonitoringView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    
    @extend_schema(
        request=TaskSubmissionSerializer,
        responses={200: TaskSubmissionSerializer , 400: TaskSubmissionSerializer.errors},
        description="Get and create monitoring records",
        tags=["TaskSubmission"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.UUID, description="ID of the monitoring record"),
            OpenApiParameter(name='request_uuid', type=uuid.UUID, description="ID of the monitoring request"),
            OpenApiParameter(name='approval_status', type=str, description="Approval status of the monitoring record"),
        ],
    )
    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = TaskSubmission.objects.all().order_by('-updated_at')
            serializer = TaskSubmissionSerializer(monitoring, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='supervisor').exists():
            monitoring = TaskSubmission.objects.filter(user=request.user).order_by('-updated_at')
            approval_status = request.query_params.get('approval_status',None)
            if approval_status:
                monitoring = monitoring.filter(approval_status=approval_status).order_by('-updated_at')
            if request.query_params.get('uuid'):
                monitoring = monitoring.filter(uuid=request.query_params.get('uuid'))
                if not monitoring.exists():
                    return Response({"error": "TaskSubmission record not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    monitoring = monitoring.first()
                    serializer = TaskSubmissionSerializer(monitoring)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            elif request.query_params.get('request_uuid'):
                monitoring_request = get_object_or_404(TaskSubmissionRequest, uuid=request.query_params.get('request_uuid'))
                monitoring = monitoring.filter(billboard=monitoring_request.billboards, user=monitoring_request.user).order_by('-created_at')
                if not monitoring.exists():
                    return Response({"error": "TaskSubmission record not found"}, status=status.HTTP_404_NOT_FOUND)
                serializer = TaskSubmissionSerializer(monitoring, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer = TaskSubmissionSerializer(monitoring, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
        
    @extend_schema(
    request=TaskSubmissionSerializer,
    responses={200: TaskSubmissionSerializer, 400: TaskSubmissionSerializer.errors},
    description="Update a monitoring record",
    tags=["TaskSubmission"],
    )
    def patch(self, request):
        # Ensure permission check for 'supervisor' and 'admin' groups
        if not request.user.groups.filter(name__in=['supervisor', 'admin']).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
        # Get the UUID from request data
        uuid = request.data.get('uuid', None)
        
        if not uuid:
            return Response({"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the TaskSubmission object by UUID
            monitoring = TaskSubmission.objects.get(uuid=uuid)
        except TaskSubmission.DoesNotExist:
            return Response({"error": "TaskSubmission object not found"}, status=status.HTTP_404_NOT_FOUND)

        # Save old status for notification
        old_status = monitoring.approval_status

        # Make request.data mutable and add user_id
        data = request.data.copy()
        if request.user.groups.filter(name='admin').exists():
            data['user_id'] = data.get('user_id')
        else:
            data['user_id'] = request.user.id

        # Ensure the billboard and UUID are added to data
        data['billboard'] = str(monitoring.billboard.uuid)  # Pass UUID if serializer expects it
        data['uuid'] = str(monitoring.uuid)

        # Initialize the serializer with partial update
        serializer = TaskSubmissionSerializer(monitoring, data=data, partial=True)
        tasksubmission = TaskSubmissionRequest.objects.filter(task_list__in=[monitoring]).first()
        if tasksubmission.task_list.filter(front__isnull=False,close__isnull=False,left__isnull=False,right__isnull=False,status__isnull=False,comment__isnull=False).exists() ==False:
            tasksubmission.is_accepeted = 'COMPLETED'
            tasksubmission.save()

        if serializer.is_valid():
            # Save the updated monitoring object
            serializer.save()
            # Send notification if status changed
            new_status = serializer.instance.approval_status
            if old_status != new_status:
                notif = Notification.objects.create(
                    user=serializer.instance.user,
                    message=f"Your task submission status changed from {old_status} to {new_status}.",
                    type='task'
                )
                self.send_realtime_notification(serializer.instance.user.id, {
                    "message": notif.message,
                    "type": notif.type,
                    "created_at": str(notif.created_at),
                    "is_read": notif.is_read,
                })
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_realtime_notification(self, user_id, content):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_notification",
                "content": content,
            }
        )

    def post(self, request):
        # Ensure permission check for 'supervisor' and 'admin' groups
        if not request.user.groups.filter(name__in=['supervisor', 'admin']).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)

        # Make request.data mutable and add user_id
        data = request.data.copy()
        if request.user.groups.filter(name='admin').exists():
            data['user_id'] = data.get('user_id')
        else:
            data['user_id'] = request.user.id

        # Initialize the serializer with partial update
        uuid_list = data.pop('uuid', None)
        if isinstance(uuid_list, list):
            uuid = uuid_list[0]
        else:
            uuid = uuid_list
        serializer = TaskReSubmissionSerializer(data=data)
        
        
        if serializer.is_valid():
            # Save the updated monitoring object
            task = TaskSubmission.objects.filter(uuid=uuid).first()
            tasksubmissionrequest = TaskSubmissionRequest.objects.filter(task_list__in=[task])
            if tasksubmissionrequest.exists():
                tasksubmissionrequest = tasksubmissionrequest.first()
            serializer.save()
            tasksubmissionrequest.task_list.add(serializer.instance)
            tasksubmissionrequest.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

