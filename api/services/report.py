from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter,OpenApiResponse
from django.db.models import F, Sum
from api.models import Campaign, Impression, Impression_Detail
from django.utils import timezone


class ReportService:
    def get_impressions_report(self, start_date=None, end_date=None):
        try:
            # Make sure dates are timezone-aware
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
                start_date = timezone.make_aware(start_date)
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = timezone.make_aware(end_date)

            impressions_list = Impression.objects.all()
            if start_date:
                impressions_list = impressions_list.filter(date__gte=start_date)
            if end_date:
                impressions_list = impressions_list.filter(date__lte=end_date)

            # Get total impressions
            total_impressions = impressions_list.aggregate(total=Sum('impressions'))['total'] or 0

            # Get date-wise total impressions
            date_wise_total_impressions = impressions_list.annotate(
                date=F('date')
            ).annotate(
                total_impressions=Sum('impressions')
            )

            # Get vehicle type wise impressions
            vehicle_type_impressions = Impression_Detail.objects.filter(
                impression__in=impressions_list
            ).values('vehicle_type').annotate(
                total=Sum('vehicle_count')
            )

            return {
                'total_impressions': total_impressions,
                'date_wise_impressions': list(date_wise_total_impressions.values('date', 'total_impressions')),
                'vehicle_type_impressions': list(vehicle_type_impressions)
            }
        except Exception as e:
            return {'error': str(e)}


class CalculateReportView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Calculate Report",
        description="Calculate Report",
        parameters=[
            OpenApiParameter(name="uuid", description="UUID of the campaign", required=True, type=str),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Report calculated successfully"),
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="No impressions found"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="UUID is required"),
        }
    )
    def get(self, request):
        uuid = request.query_params.get('uuid')
        start_date = request.query_params.get('start_date',None)
        end_date = request.query_params.get('end_date',None)
        
        
        if not uuid:
            return Response({"message": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        campaign = get_object_or_404(Campaign, uuid=uuid)
        billboards_data = campaign.campaigns_time.all()
        date_wise_vehicle_wise_data = []
        date_wise_data = []
        hour_wise_impressions = []
        total_impressions = 0
        temp_data = []
        card_data = {}
        total_billboard_data = 0
        ots = timezone.now()
        lts = timezone.now()
        billboard_wise_data = []
        
        for billboard_data in billboards_data:
            impressions_list = Impression.objects.filter(
                billboard=billboard_data.billboard,
                date__gte=billboard_data.start_time,
                date__lt=billboard_data.end_time
            ).order_by('date')
            if start_date:
                impressions_list = impressions_list.filter(date__gte=start_date)
            if end_date:
                impressions_list = impressions_list.filter(date__lte=end_date)
            
            if impressions_list.exists():
                # Get vehicle type wise data
                impressions_lists = impressions_list.values('date').annotate(
                    vehicle_type=F('impression_detail__vehicle_type')
                ).annotate(
                    vehicle_count=Sum('impression_detail__vehicle_count')
                )
                date_wise_vehicle_wise_data.append(impressions_lists)
                billboard_wise_data.append({
                    'uuid': impressions_list.first().billboard.uuid,
                    'impressions': impressions_list.aggregate(impressions=Sum('impressions'))['impressions'],
                    'reach': int(impressions_list.aggregate(impressions=Sum('impressions'))['impressions'] / billboards_data.count())
                })
                
                # Calculate averages
                temp_data.append(impressions_list.aggregate(
                    dwalltime=Sum('dwalltime')/impressions_list.count(),
                    frequency=Sum('frequency')
                ))
                total_billboard_data += 1
                hour_wise_impressions.append(impressions_list.values('hour').annotate(
                    impressions=Sum('impressions')
                ))
                
                # Update OTS and LTS
                if impressions_list.first().ots and impressions_list.first().ots < ots:
                    ots = impressions_list.first().ots
                if impressions_list.first().lts and impressions_list.first().lts > lts:
                    lts = impressions_list.first().lts
                
                # Get date wise total impressions
                date_wise_total_impressions = impressions_list.values('date').annotate(
                    impressions=Sum('impressions')
                )
                date_wise_data.append(date_wise_total_impressions)
                total_impressions += impressions_list.aggregate(
                    total_impressions=Sum('impressions')
                )['total_impressions']
        

        
        if not date_wise_vehicle_wise_data and not date_wise_data:
            return Response({"message": "No impressions found"}, status=status.HTTP_204_NO_CONTENT)
                # Calculate card data
        card_data = {
            'ots': ots,
            'lts': lts,
            'avg_dwalltime': sum(x['dwalltime'] for x in temp_data)/total_billboard_data if temp_data else 0,
            'total_frequency': sum(x['frequency'] for x in temp_data)/total_billboard_data if temp_data else 0,
            'total_impressions': total_impressions,
            'total_billboards': billboards_data.count(),
            'total_date': len(date_wise_data[0])
        }
        return Response({
            "message": "Report calculated successfully",
            "vehicale_data": date_wise_vehicle_wise_data[0],
            "date_wise_data": date_wise_data[0],
            'card_data': card_data,
            'hour_wise_impressions': hour_wise_impressions[0],
            'billboard_wise_data': billboard_wise_data
        }, status=status.HTTP_200_OK)
    
    

