
from api.models import Monitoring,BILLBOARD_STATUS,Supervisor
from api.serializer import MonitoringSerializer
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




class BillboardStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='status', type=str, description="Status of the billboard"),
        ],
        responses={
            200: OpenApiResponse(description="Billboard status"),
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
    
    @extend_schema(
        request=MonitoringSerializer,
        responses={200: MonitoringSerializer, 400: MonitoringSerializer.errors},
        description="Get and create monitoring records",
        tags=["Monitoring"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.uuid4, description="ID of the monitoring record"),
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
            else:
                serializer = MonitoringSerializer(monitoring, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        
    @extend_schema(
        request=MonitoringSerializer,
        responses={201: MonitoringSerializer, 400: MonitoringSerializer.errors},
        description="Create a new monitoring record",
        tags=["Monitoring"],
    )
   
    def put(self, request):
        if request.user.groups.filter(name='supervisor').exists() or request.user.groups.filter(name='admin').exists():
            try:
                uuid = request.data.get('uuid')
                if not uuid:
                    return Response({"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)

                monitoring = Monitoring.objects.get(uuid=uuid)

                if(request.user.groups.filter(name='admin').exists()):
                    request.data['user'] = request.data.get('user_id')
                else:
                    request.data['user'] = request.user.id
                request.data['billboard'] = monitoring.billboard.id  
                request.data['uuid'] = uuid  

                serializer = MonitoringSerializer(monitoring, data=request.data, partial=True)

                if serializer.is_valid():
                    serializer.save(user=request.user)
                    return Response(serializer.data, status=status.HTTP_200_OK)  
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            except Monitoring.DoesNotExist:
                return Response({"error": "Monitoring object not found"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
               
            
