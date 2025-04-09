

from datetime import datetime, timedelta, timezone
import json
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
import base64
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Sum,Avg
from drf_spectacular.utils import extend_schema, OpenApiParameter,OpenApiResponse


from ..serializer import *
class LoginApiView(APIView):
    serializer_class = TokenAuth

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token = serializer.get_token(user)


        return Response({
            "status": "Login Successful",
            "access_token":str(token.access_token),
            "groups" : user.groups.first().name,


        }, status=status.HTTP_200_OK)
        
        
class LogoutApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.blacklist()
        return Response({"status": "Logout Successful"}, status=status.HTTP_200_OK)
    