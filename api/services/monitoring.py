
from api.models import TaskSubmission,BILLBOARD_STATUS,TaskSubmissionRequest
from api.serializer import TaskSubmissionSerializer
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

from rest_framework import viewsets





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
        ],
    )
    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = TaskSubmission.objects.all()
            serializer = TaskSubmissionSerializer(monitoring, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='supervisor').exists():
            monitoring = TaskSubmission.objects.filter(user=request.user)
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
        print(request.FILES)  # Debugging output to inspect incoming request data
        
        if not uuid:
            return Response({"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the TaskSubmission object by UUID
            monitoring = TaskSubmission.objects.get(uuid=uuid)
        except TaskSubmission.DoesNotExist:
            return Response({"error": "TaskSubmission object not found"}, status=status.HTTP_404_NOT_FOUND)

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

        if serializer.is_valid():
            # Save the updated monitoring object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

