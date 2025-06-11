import json
from api.models import TaskSubmission,BILLBOARD_STATUS,Monitor,TaskSubmissionRequest
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
from django.utils import timezone
from api.serializer import CampaignSerializer
from api.models import Campaign

class CampaignApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=CampaignSerializer,
        responses={200: CampaignSerializer, 400: CampaignSerializer.errors},
        description="Get and create campaign records",
        tags=["Campaign"],
        parameters=[
            OpenApiParameter(name='uuid', type=uuid.UUID, description="ID of the campaign record"),
        ],
    )
    def get(self, request):
        uuid = request.query_params.get('uuid', None)
        if request.user.groups.filter(name='admin').exists():
            campaigns = Campaign.objects.all()
            if uuid:
                campaigns = campaigns.filter(uuid=uuid)
            serializer = CampaignSerializer(campaigns, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='supervisor').exists():
            campaigns = Campaign.objects.filter(user=request.user)
            if uuid:
                campaigns = campaigns.filter(uuid=uuid)
            if request.query_params.get('uuid'):
                campaigns = campaigns.filter(uuid=request.query_params.get('uuid'))
            serializer = CampaignSerializer(campaigns, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)
    @extend_schema(
        request=CampaignSerializer,
        responses={201: CampaignSerializer, 400: CampaignSerializer.errors},
        description="Create a new campaign record",
        summary="FromData",
        tags=["Campaign"],
    )
    def post(self, request):
        # Create a mutable copy of the data
        data = request.data.copy()
        
        # Get user from request data or use authenticated user
        user = request.data.get('user', None)
        if not user:
            user = request.user

        # Set user_id for the serializer
        data['user'] = user.id if isinstance(user, User) else user
        
        raw_input = data.get('campaigns_time_input')

        if isinstance(raw_input, str):
            try:
                data['campaigns_time_input'] = json.dumps({
                    'data': raw_input
                })
                
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON in campaigns_time_input"}, status=400)

    
        serializer = CampaignSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Serializer errors:", serializer.errors)  # Debug print
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        request=CampaignSerializer,
        responses={200: CampaignSerializer, 400: CampaignSerializer.errors},
        description="Update a campaign record",
        tags=["Campaign"],
    )
    def patch(self, request):
        if request.user.groups.filter(name='admin').exists():
            campaign = get_object_or_404(Campaign, uuid=request.data['uuid'])
            serializer = CampaignSerializer(campaign, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)
    @extend_schema(
        request=CampaignSerializer,
        responses={200: CampaignSerializer, 400: CampaignSerializer.errors},
        description="Delete a campaign record",
        tags=["Campaign"],
    )
    def delete(self, request):
        if request.user.groups.filter(name='admin').exists():
            campaign = get_object_or_404(Campaign, uuid=request.data['uuid'])
            TaskSubmissionRequest.objects.filter(campaign=campaign).delete()
            campaign.delete()
            return Response({"message": "Campaign deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You are not authorized to view this data"}, status=status.HTTP_401_UNAUTHORIZED)