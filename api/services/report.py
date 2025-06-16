from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter,OpenApiResponse
from django.db.models import F, Sum, Value, JSONField
from api.models import Campaign, Impression, Impression_Detail, Billboard
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
        start_time = request.query_params.get('start_time',None)
        end_time = request.query_params.get('end_time',None)
        location = request.query_params.get('location',None)
        billboard_type = request.query_params.get('billboard_type',None)
        time_slot = request.query_params.get('time_slots',None)
        timeSlots = {
         'early_morning': [3, 4, 5,6],
         'morning': [ 7, 8, 9, 10, 11],
         'afternoon': [12, 13, 14, 15, 16],
         'evening': [17, 18, 19, 20, 21, 22, 23, 0, 1, 2],
       }
        
        
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
        location_wise_data = []
        area_wise_data = []
        
        all_billboards_impressions = Impression.objects.filter(
            billboard__in=billboards_data.values_list('billboard', flat=True)
        ).order_by('date')
        if start_date:
            all_billboards_impressions = all_billboards_impressions.filter(date__gte=start_date)
        if end_date:
            all_billboards_impressions = all_billboards_impressions.filter(date__lt=end_date)
        if start_time:
            all_billboards_impressions = all_billboards_impressions.filter(hour__gte=start_time)
        if end_time:
            all_billboards_impressions = all_billboards_impressions.filter(hour__lte=end_time)
        if time_slot:
            time_slot_list = [time for times in time_slot.split(',') for time in timeSlots[times]]
            all_billboards_impressions = all_billboards_impressions.filter(hour__in=time_slot_list)
        if location:
            location_list = location.split(';')
            all_billboards_impressions = all_billboards_impressions.filter(billboard__location__location__in=location_list)
        if billboard_type:
            all_billboards_impressions = all_billboards_impressions.filter(billboard__views__billboard_type=billboard_type)
            
        for billboard_data in billboards_data:
            impressions_list = all_billboards_impressions.filter(
                billboard=billboard_data.billboard
            )
            
            if impressions_list.exists():
                # Get vehicle type wise data
                impressions_lists = impressions_list.values('date').annotate(
                    vehicle_type=F('impression_detail__vehicle_type')
                ).annotate(
                    vehicle_count=Sum('impression_detail__vehicle_count')
                )
                date_wise_vehicle_wise_data.append(impressions_lists)
                billboard_wise_data.append({
                    'uuid': billboard_data.billboard.uuid,
                    'impressions': impressions_list.aggregate(impressions=Sum('impressions'))['impressions'] or 0,
                    'reach': int((impressions_list.aggregate(impressions=Sum('impressions'))['impressions'] or 0) / billboards_data.count())
                })
           
                # Calculate averages
       
                total_billboard_data += 1

               
                
                # Update OTS and LTS
                if impressions_list.first().ots and impressions_list.first().ots < ots:
                    ots = impressions_list.first().ots
                if impressions_list.first().lts and impressions_list.first().lts > lts:
                    lts = impressions_list.first().lts
                
                # Get date wise total impressions

                total_impressions += impressions_list.aggregate(
                    total_impressions=Sum('impressions')
                )['total_impressions']
        

        
        if not all_billboards_impressions:
            return Response({"message": "No impressions found"}, status=status.HTTP_204_NO_CONTENT)

        location_wise_data.append(all_billboards_impressions.values('billboard__location__division').annotate(
                    impressions=Sum('impressions')
                ).values('billboard__location__division', 'impressions').annotate(
                    location=F('billboard__location__division')
                ).values('location', 'impressions'))
        hour_wise_impressions.append(all_billboards_impressions.values('hour').annotate(
                    impressions=Sum('impressions')
                ))  
        date_wise_data.append(all_billboards_impressions.values('date').annotate(
                    impressions=Sum('impressions')
                ))
        area_wise_data.append(all_billboards_impressions.values('billboard__location__town_class', 'billboard__location__thana').annotate(
                    impressions=Sum('impressions')
                ).values('billboard__location__town_class', 'billboard__location__thana', 'impressions').annotate(
                    area=F('billboard__location__town_class')
                ).values('area', 'billboard__location__thana', 'impressions'))
        temp_data.append(all_billboards_impressions.aggregate(
                    dwalltime=Sum('dwalltime')/all_billboards_impressions.count(),
                    frequency=Sum('frequency')
                ))
        card_data = {
            'ots': ots,
            'lts': lts,
            'avg_dwalltime': round(sum(x['dwalltime'] for x in temp_data)/total_billboard_data, 2) if temp_data else 0,
            'total_frequency': round(sum(x['frequency'] for x in temp_data)/total_billboard_data, 0) if temp_data else 0,
            'total_impressions': total_impressions,
            'total_billboards': billboards_data.count(),
            'total_date': len(date_wise_data[0])
        }
        # Format area_wise_data
        formatted_area_data = []
        area_dict = {}
        
        for area_group in area_wise_data:
            for item in area_group:
                area = item['area']
                if area not in area_dict:
                    area_dict[area] = {
                        'area': area,
                        'data': []
                    }
                
                # Check if location already exists
                location_exists = False
                for loc_data in area_dict[area]['data']:
                    if loc_data['location'] == item['billboard__location__thana']:
                        loc_data['impressions'] += item['impressions']
                        location_exists = True
                        break
                
                if not location_exists:
                    area_dict[area]['data'].append({
                        'location': item['billboard__location__thana'],
                        'impressions': item['impressions']
                    })
        
        formatted_area_data = list(area_dict.values())

        # Format location_wise_data
        location_dict = {}
        for location_group in location_wise_data:
            for item in location_group:
                location = item['location']
                if location not in location_dict:
                    location_dict[location] = {
                        'location': location,
                        'impressions': 0
                    }
                location_dict[location]['impressions'] += item['impressions']
        
        formatted_location_data = list(location_dict.values())

        return Response({
            "message": "Report calculated successfully",
            "vehicale_data": date_wise_vehicle_wise_data[0],
            "date_wise_data": date_wise_data[0],
            'card_data': card_data,
            'hour_wise_impressions': hour_wise_impressions[0],
            'billboard_wise_data': billboard_wise_data,
            'location_wise_data': formatted_location_data,
            'area_wise_data': formatted_area_data
        }, status=status.HTTP_200_OK)
        
class UploadReportView(APIView):
    
    @extend_schema(
        summary="Upload Report",
        description="Upload Report",
        
    )
    def post(self, request):
        data = request.data
        for item in data:
            #get or create impression
            impression, created = Impression.objects.get_or_create(
                billboard=Billboard.objects.get(uuid=item['billboard']),
                date=item['date'],
                hour=item['hour'],
            )

            if created:
                impression.impressions = 1
                impression.ots = timezone.now()
                impression.lts = timezone.now()
                impression.dwalltime = item['dwalltime']
                impression.frequency = 0
            else:
                impression.impressions += 1
                impression.frequency += 1
                impression.lts = timezone.now()
                impression.dwalltime = (
                    float(item['dwalltime']) + float(impression.dwalltime)
                ) / 2
            impression.save()
                
        return Response({"message": "Report updated successfully"}, status=status.HTTP_200_OK)
    
    

