
from api.models import Monitoring,BILLBOARD_STATUS,MonitoringRequest
from api.serializer import MonitoringSerializer
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
        request=MonitoringSerializer,
        responses={200: MonitoringSerializer , 400: MonitoringSerializer.errors},
        description="Get and create monitoring records",
        tags=["Monitoring"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.UUID, description="ID of the monitoring record"),
            OpenApiParameter(name='request_uuid', type=uuid.UUID, description="ID of the monitoring request"),
        ],
    )
    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = Monitoring.objects.all()
            serializer = MonitoringSerializer(monitoring, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='supervisor').exists():
            monitoring = Monitoring.objects.filter(user=request.user)
            if request.query_params.get('uuid'):
                monitoring = monitoring.filter(uuid=request.query_params.get('uuid'))
                if not monitoring.exists():
                    return Response({"error": "Monitoring record not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    monitoring = monitoring.first()
                    serializer = MonitoringSerializer(monitoring)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            elif request.query_params.get('request_uuid'):
                monitoring_request = get_object_or_404(MonitoringRequest, uuid=request.query_params.get('request_uuid'))
                monitoring = monitoring.filter(billboard=monitoring_request.billboards, user=monitoring_request.user).order_by('-created_at')
                if not monitoring.exists():
                    return Response({"error": "Monitoring record not found"}, status=status.HTTP_404_NOT_FOUND)
                serializer = MonitoringSerializer(monitoring, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer = MonitoringSerializer(monitoring, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
        
    @extend_schema(
    request=MonitoringSerializer,
    responses={200: MonitoringSerializer, 400: MonitoringSerializer.errors},
    description="Update a monitoring record",
    tags=["Monitoring"],
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
            # Get the Monitoring object by UUID
            monitoring = Monitoring.objects.get(uuid=uuid)
        except Monitoring.DoesNotExist:
            return Response({"error": "Monitoring object not found"}, status=status.HTTP_404_NOT_FOUND)

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
        serializer = MonitoringSerializer(monitoring, data=data, partial=True)

        if serializer.is_valid():
            # Save the updated monitoring object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MonitoringViewSet(viewsets.ModelViewSet):
    queryset = Monitoring.objects.all()
    serializer_class = MonitoringSerializer
    parser_classes = [MultiPartParser, FormParser]

    def partial_update(self, request, pk=None):
        # Ensure permission check for 'supervisor' and 'admin' groups
        if not request.user.groups.filter(name__in=['supervisor', 'admin']).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the Monitoring object by UUID
        uuid = request.data.get('uuid')
        if not uuid:
            return Response({"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            monitoring = Monitoring.objects.get(uuid=uuid)
        except Monitoring.DoesNotExist:
            return Response({"error": "Monitoring object not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare data for serialization
        data = request.data.copy()
        data['user_id'] = request.user.id if not request.user.groups.filter(name='admin').exists() else data.get('user_id')
        data['billboard'] = str(monitoring.billboard.uuid)
        data['uuid'] = str(monitoring.uuid)

        # Initialize the serializer with partial=True to allow partial updates
        serializer = self.get_serializer(monitoring, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)