from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, timezone

from api.models import Cv, Billboard_View, Billboard, Impression
from api.serializer import CvSerializer

class CvApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CvSerializer,
        responses={200: CvSerializer, 400: CvSerializer.errors},
        description="Get and create Cv records",
        tags=["Cv"],
        parameters=[
            OpenApiParameter(name='id', type=int, description="ID of the Cv", required=False),
        ],
    )
    def get(self, request):
        cvs = Cv.objects.all()
        if request.query_params.get('id'):
            cvs = cvs.filter(id=request.query_params.get('id'))
        serializer = CvSerializer(cvs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CvSerializer,
        responses={200: CvSerializer, 400: CvSerializer.errors},
        description="Create a new Cv record",
        tags=["Cv"],
    )
    def post(self, request):
        data = request.data
        view = get_object_or_404(Billboard_View, camera_id=data['camera_id'])
        billboard = get_object_or_404(Billboard, view=view.id)
        data['billboard'] = billboard.id
        data['view'] = view.id
        serializer = CvSerializer(data=request.data,many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CvSerializer,
        responses={200: CvSerializer, 400: CvSerializer.errors},
        description="Update a Cv record",
        tags=["Cv"],
    )
    def patch(self, request):
        cv = get_object_or_404(Cv, id=request.data['id'])
        serializer = CvSerializer(cv, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class UpdateImpressionModelAfterEvery1Hr():

    def get(self, request):
        cvs = Cv.objects.all()
        for cv in cvs:
            #cv.entry_time is in DateTimeField
            hour = cv.entry_time.hour
            date = cv.entry_time.date()
            impression = Impression.objects.filter(billboard=cv.billboard, hour=hour, date=date)
            if impression:
                impression.first().impressions += 1
                impression.first().impression_detail.create(vehicle_type=cv.object_type )
                impression.first().dwalltime += cv.dwell_time
                impression.first().frequency += 1
                impression.first().lts = cv.exit_time
                if impression.first().impression_detail.filter(vehicle_type=cv.object_type).exists():
                    impression.first().impression_detail.filter(vehicle_type=cv.object_type).first().vehicle_count += 1
                    impression.first().impression_detail.filter(vehicle_type=cv.object_type).first().updated_at = timezone.now()
                    
                    # Make sure both datetimes are timezone-aware before comparison
                    entry_time = cv.entry_time
                    exit_time = cv.exit_time
                    
                    if impression.first().ots and impression.first().ots < entry_time:
                        impression.first().ots = entry_time
                    if impression.first().lts and impression.first().lts > exit_time:
                        impression.first().lts = exit_time
                        
                    impression.first().impression_detail.filter(vehicle_type=cv.object_type).first().save()
                
                else:
                    impression.first().impression_detail.create(vehicle_type=cv.object_type, vehicle_count=1)
                impression.first().save()
            else:
                impression = Impression.objects.create(billboard=cv.billboard, hour=hour, date=date, impressions=1,dwalltime=cv.dwalltime,frequency=cv.frequency,ots=cv.entry_time,lts=cv.exit_time)
                impression.impression_detail.create(vehicle_type=cv.object_type, vehicle_count=1)
                impression.save()
        cv.delete()
        return Response({"message": "Impression model updated successfully"}, status=status.HTTP_200_OK)
