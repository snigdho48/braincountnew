from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter,OpenApiResponse
from django.db.models import F, Sum, Value, JSONField, Avg, Max, Min
from api.models import Campaign, Impression, Impression_Detail, Billboard, Impression_Reach_Id
from django.utils import timezone
from statistics import mean



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
         'early_morning': [0, 1, 2, 3, 4, 5, 6],
         'morning': [ 7, 8, 9, 10, 11,12],
         'afternoon': [ 13, 14, 15, 16,17,18],
         'evening': [ 19, 20, 21, 22, 23],
       }
        
        
        if not uuid:
            return Response({"message": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        campaign = get_object_or_404(Campaign, uuid=uuid)
        billboards_data = campaign.campaigns_time.all()
        date_wise_vehicle_wise_data = []
        date_wise_data = []
        hour_wise_impressions = []
        total_impressions = 0

        card_data = {}
        total_billboard_data = 0
        ots = 0
        lts = 0
        billboard_wise_data = []
        location_wise_data = []
        area_wise_data = []
        # unique billboard data
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
            all_billboards_impressions = all_billboards_impressions.filter(billboard__location__division__in=location_list)
        if billboard_type:
            billboard_type_list = billboard_type.split(',')
            all_billboards_impressions = all_billboards_impressions.filter(billboard__views__billboard_type__in=billboard_type_list)
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
                    'reach': impressions_list.values_list('reach__reach_id',flat=True).distinct().count() or 0
                })
           
                # Calculate averages
       
                total_billboard_data += 1
                ots += impressions_list.aggregate(ots=Sum('ots'))['ots'] or 0
                lts += impressions_list.aggregate(lts=Sum('lts'))['lts'] or 0
                
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
        print(all_billboards_impressions.values_list('reach__reach_id',flat=True).count())

        card_data = {
            'ots': round(ots/total_billboard_data, 0),
            'lts': round(lts/total_billboard_data, 0),
            'avg_dwalltime': round(mean(all_billboards_impressions.values_list('dwalltime', flat=True)), 2) if all_billboards_impressions else 0,
            'total_frequency': all_billboards_impressions.values_list('reach__reach_id',flat=True).distinct().count() if all_billboards_impressions else 0,
            'total_impressions': total_impressions,
            'total_billboards': billboards_data.values_list('billboard', flat=True).distinct().count(),
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

        # Format hour_wise_impressions
        hour_dict = {}
        for hour_group in hour_wise_impressions:
            for item in hour_group:
                hour = item['hour']
                if hour not in hour_dict:
                    hour_dict[hour] = {
                        'hour': hour,
                        'impressions': 0
                    }
                hour_dict[hour]['impressions'] += item['impressions']
        
        formatted_hour_data = list(hour_dict.values())
        all_billboards_division_distinct = list(set(all_billboards_impressions.values_list('billboard__location__division',flat=True).distinct()))
        all_billboards_type_distinct = list(set(all_billboards_impressions.values_list('billboard__views__billboard_type', flat=True)))
        

        return Response({
            "message": "Report calculated successfully",
            "vehicale_data": date_wise_vehicle_wise_data[0],
            "date_wise_data": date_wise_data[0],
            'card_data': card_data,
            'hour_wise_impressions': formatted_hour_data,
            'billboard_wise_data': billboard_wise_data,
            'location_wise_data': formatted_location_data,
            'area_wise_data': formatted_area_data,
            'divisions': all_billboards_division_distinct
        }, status=status.HTTP_200_OK)
        
class UploadReportView(APIView):
    
    @extend_schema(
        summary="Upload Report",
        description="Upload Report",
        
    )
    def post(self, request):
        data = request.data
        billboard_cache = {}
        CHUNK_SIZE = 100  # Process 100 records at a time
        
        # First pass: collect all billboards
        print("Collecting billboards...")
        for item in data:
            uuid = item['billboard']
            if uuid not in billboard_cache:
                billboard_cache[uuid] = Billboard.objects.get(uuid=uuid)
        
        # Process data in chunks
        total_chunks = (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE
        for chunk_idx in range(total_chunks):
            print(f"Processing chunk {chunk_idx + 1}/{total_chunks}")
            start_idx = chunk_idx * CHUNK_SIZE
            end_idx = min((chunk_idx + 1) * CHUNK_SIZE, len(data))
            chunk_data = data[start_idx:end_idx]
            
            reach_ids_to_create = []
            impressions_to_create = []
            impressions_to_update = []
            
            # Process chunk
            for item in chunk_data:
                billboard = billboard_cache[item['billboard']]
                
                # Parse reach IDs
                reach_ids = [id.strip().strip("'") for id in item['reach'].strip('[]').split('\n')]
                
                # Check if impression exists
                impression = Impression.objects.filter(
                    billboard=billboard,
                    date=item['date'],
                    hour=item['hour']
                )

                if not impression.exists():
                    # Create new impression
                    new_impression = Impression(
                        billboard=billboard,
                        date=item['date'],
                        hour=item['hour'],
                        impressions=item['impressions'],
                        ots=1,
                        lts=1,
                        dwalltime=float(item['dwalltime']),
                        frequency=0
                    )
                    impressions_to_create.append(new_impression)
                    # Store reach IDs for bulk creation
                    for reach_id in reach_ids:
                        reach_ids_to_create.append(Impression_Reach_Id(reach_id=reach_id))
                else:
                    # Update existing impression
                    impression = impression.first()
                    impression.impressions += item['impressions']
                    impression.ots += 1
                    impression.lts += 1
                    impression.dwalltime = mean([impression.dwalltime, float(item['dwalltime'])])
                    impressions_to_update.append(impression)
                    # Store reach IDs for bulk creation
                    for reach_id in reach_ids:
                        reach_ids_to_create.append(Impression_Reach_Id(reach_id=reach_id))

            # Bulk create reach IDs
            created_reach_ids = Impression_Reach_Id.objects.bulk_create(reach_ids_to_create)

            # Bulk create new impressions
            created_impressions = Impression.objects.bulk_create(impressions_to_create)

            # Bulk update existing impressions
            if impressions_to_update:
                Impression.objects.bulk_update(
                    impressions_to_update,
                    ['impressions', 'ots', 'lts', 'dwalltime']
                )

            # Create many-to-many relationships
            for impression in created_impressions + impressions_to_update:
                # Get the reach IDs for this impression
                impression_reach_ids = created_reach_ids[:len(reach_ids)]
                created_reach_ids = created_reach_ids[len(reach_ids):]
                impression.reach.add(*impression_reach_ids)

        return Response({
            "message": "Report uploaded successfully"
        }, status=status.HTTP_200_OK)
    
class ImpreessionDetailView(APIView):

    def get(self, request):
        billboard_map = [
            'ad90ef64-7617-42a2-86b2-919701d03669',
            'd1899d57-7140-4be9-a246-b8361bda3b0e',
            '06b9fe55-0264-40c9-893d-b5e1142189d7',
            '59d6b25c-d1f5-4921-b2a9-ffb352df4fee',
        ]
        impressions = Impression.objects.filter(billboard__uuid__in=billboard_map)
        impressions.delete()
        return Response({"message": "Impressions fetched successfully", "impressions": impressions}, status=status.HTTP_200_OK)
    
    

