
from api.models import Monitoring,BILLBOARD_STATUS
from api.serializer import MonitoringSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
import base64
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated



class BillboardStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"status": BILLBOARD_STATUS}, status=status.HTTP_200_OK)
    
class MonitoringView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.groups.filter(name='admin').exists():
            monitoring = Monitoring.objects.all()
            serializer = MonitoringSerializer(monitoring, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='Supervisor').exists():
            monitoring = Monitoring.objects.filter(user=request.user)
            serializer = MonitoringSerializer(monitoring, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
    def post(self, request):
        if request.user.groups.filter(name='Supervisor').exists():
            serializer = MonitoringSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
