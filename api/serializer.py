import json
from rest_framework import serializers
from django.contrib.auth.models import User,Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_field
from collections import defaultdict



class TokenAuth(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        user_groups = [group.name for group in user.groups.all()]
        token['user_groups'] = user_groups
        return token

    def validate(self, attrs):
        credentials = {
            'username': attrs.get('username'),
            'password': attrs.get('password')
        }

        if not all(credentials.values()):
            raise serializers.ValidationError(
                'Must include "username" and "password".'
            )

        try:
            user = User.objects.get(username=credentials['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect "username" or "password".'
            )

        if not user.check_password(credentials['password']):
            raise serializers.ValidationError(
                'Incorrect "username" or "password".'
            )

        attrs['user'] = user
        return attrs

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name'] 
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        
class Billboard_infoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billboard_info
        fields = '__all__'
class Billboard_ViewSerializer(serializers.ModelSerializer):
    details = Billboard_infoSerializer(required=False, allow_null=True)
    class Meta:
        model = Billboard_View
        fields = '__all__'
        

class BillboardSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=False, allow_null=True)
    views = Billboard_ViewSerializer(required=False, allow_null=True, many=True)
    class Meta:
        model = Billboard
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
        }
        
class StuffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Stuff
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
        }

class CustomBillboardSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=False, allow_null=True)
    views = serializers.SerializerMethodField(required=False, allow_null=True)
    class Meta:
        model = Billboard
        fields = ['uuid',  'title', 'location', 'views','latitude','longitude']

    def get_views(self, obj):
        billboard_views = obj.views.all()
        senddata = []
        for billboard_view in billboard_views:
            senddata.append({
                'id': billboard_view.id,
                'billboard_type': billboard_view.billboard_type,
                'status': billboard_view.status,
                'category': billboard_view.category,
                'front': billboard_view.front.url if billboard_view.front else None,
                'left': billboard_view.left.url if billboard_view.left else None,
                'right': billboard_view.right.url if billboard_view.right else None,
                'close': billboard_view.close.url if billboard_view.close else None,
                'resolution': billboard_view.details.screen_resolution if billboard_view.details.screen_resolution else None,
                'height': billboard_view.details.panel_height_ft if billboard_view.details.panel_height_ft else None,
                'width': billboard_view.details.panel_width_ft if billboard_view.details.panel_width_ft else None,
                'location_type': billboard_view.details.location_type if billboard_view.details.location_type else None,
            
            })
        return senddata


class AdvertiserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Advertiser
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
        }
class TaskSubmissionExtraImagesSerializer(serializers.ModelSerializer):
    task_submission = serializers.UUIDField(source='task_submission.uuid', required=False,write_only=True)  # Accept UUID of the billboard, but do not allow changes to it
    class Meta:
        model = TaskSubmissionExtraImages
        fields = ['image', 'task_submission']


class TaskSubmissionExtraImagesSerializerDisplay(serializers.ModelSerializer):
    class Meta:
        model = TaskSubmissionExtraImages
        fields = ['image']

class TaskSubmissionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(source='user.id', write_only=True)  # Accept user ID, but do not allow changes to it
    billboard = serializers.UUIDField(source='billboard.uuid', required=False)  # Accept UUID of the billboard, but do not allow changes to it
    billboard_detail = serializers.SerializerMethodField(read_only=True)
    left = serializers.ImageField(required=False)
    front = serializers.ImageField(required=False)
    close = serializers.ImageField(required=False)
    right = serializers.ImageField(required=False)
    status = serializers.ListField(
        child=serializers.ChoiceField(choices=BILLBOARD_STATUS),
        allow_empty=False,
    )
    extra_images = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True
    )
    extra_images_list = serializers.SerializerMethodField(read_only=True)
    approval_status = serializers.CharField(required=False)
    reject_reason = serializers.CharField(required=False)
    view = serializers.SerializerMethodField(read_only=True)
    previous_status = serializers.SerializerMethodField(read_only=True)
    

    class Meta:
        model = TaskSubmission
        fields = ['user_id','visit_number', 'uuid', 'latitude', 'longitude', 'status', 'billboard', 'front', 'left', 'right', 'close', 'comment', 'created_at', 'updated_at','user','billboard_detail','extra_images','extra_images_list','approval_status','reject_reason','view','previous_status']
        extra_kwargs = {
            'user': {'required': False},
            'billboard': {'required': False},
        }
    @extend_schema_field(CustomBillboardSerializer)
    def get_billboard_detail(self, obj):
        return CustomBillboardSerializer(obj.billboard).data

    def get_previous_status(self, obj):
            tsr = TaskSubmission.objects.filter(id=obj.id).first()
            if tsr:
                return tsr.status
            else:
                return None
        
    def get_view(self, obj):
        tsr = TaskSubmissionRequest.objects.filter(task_list__in=[obj]).first()
        return tsr.view.id if tsr and tsr.view else None
    @extend_schema_field(TaskSubmissionExtraImagesSerializerDisplay(many=True))
    def get_extra_images_list(self, obj):
        extra_images = obj.extra_images.all()
        return [ img['image'] for img in TaskSubmissionExtraImagesSerializerDisplay(extra_images,many=True).data]
        
    
    def update(self, instance, validated_data):
        # Don't allow changes to the billboard
        # if logined user is not admin
        if  instance.user.groups.filter(name='admin').exists():
            instance.billboard = validated_data.get('billboard', instance.billboard)
            instance.user = validated_data.get('user', validated_data['user_id'])
        validated_data.pop('billboard', None) 
        if not (validated_data.get('front') or validated_data.get('left') or validated_data.get('right') or validated_data.get('close')):
            raise serializers.ValidationError("Please upload Images")
        if validated_data.get('status') is None:
            raise serializers.ValidationError("Please select status")
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.status = validated_data.get('status', instance.status)
        extra_images = validated_data.get('extra_images', None)
        instance.approval_status = validated_data.get('approval_status', 'PENDING')
        instance.reject_reason = validated_data.get('reject_reason', instance.reject_reason)
        if extra_images:
            for image in extra_images:
                extra_image = TaskSubmissionExtraImages.objects.create(
                    task_submission=instance,  # not instance.uuid
                    image=image
                )
                instance.extra_images.add(extra_image)

        for field in ['left', 'front', 'close', 'right']:
            if field in validated_data:
                file = validated_data.pop(field)
                setattr(instance, field, file)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()

        return instance

class TaskReSubmissionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(source='user.id', write_only=True)
    billboard = serializers.UUIDField(source='billboard.uuid', required=False)
    billboard_detail = serializers.SerializerMethodField(read_only=True)
    left = serializers.ImageField(required=False)
    front = serializers.ImageField(required=False)
    close = serializers.ImageField(required=False)
    right = serializers.ImageField(required=False)
    status = serializers.ListField(
        child=serializers.ChoiceField(choices=BILLBOARD_STATUS),
        allow_empty=False,
    )
    extra_images = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True
    )
    extra_images_list = serializers.SerializerMethodField(read_only=True)
    approval_status = serializers.CharField(required=False)
    reject_reason = serializers.CharField(required=False)

    class Meta:
        model = TaskSubmission
        fields = [
            'user_id', 'uuid', 'latitude', 'longitude', 'status', 'billboard', 
            'front', 'left', 'right', 'close', 'comment', 'created_at', 'updated_at',
            'user', 'billboard_detail', 'extra_images', 'extra_images_list',
            'approval_status', 'reject_reason','visit_number'
        ]
        extra_kwargs = {
            'user': {'required': False},
            'billboard': {'required': False},
        }

    @extend_schema_field(CustomBillboardSerializer)
    def get_billboard_detail(self, obj):
        return CustomBillboardSerializer(obj.billboard).data

    @extend_schema_field(TaskSubmissionExtraImagesSerializerDisplay(many=True))
    def get_extra_images_list(self, obj):
        extra_images = obj.extra_images.all()
        return [img['image'] for img in TaskSubmissionExtraImagesSerializerDisplay(extra_images, many=True).data]

    def create(self, validated_data):
        # Get user
        user_id = validated_data.pop('user', {}).get('id')
        user = User.objects.get(id=user_id)

        # Get billboard if provided
        billboard_data = validated_data.pop('billboard', None)
        billboard = None
        if billboard_data:
            billboard = Billboard.objects.get(uuid=billboard_data['uuid'])

        # Handle extra images
        extra_images = validated_data.pop('extra_images', None)

        # Validation
        if not any(validated_data.get(field) for field in ['front', 'left', 'right', 'close']):
            raise serializers.ValidationError("Please upload at least one of left, front, close, or right images.")
        if validated_data.get('status') is None:
            raise serializers.ValidationError("Please select a status.")

        # Create TaskSubmission
        task_submission = TaskSubmission.objects.create(
            user=user,
            billboard=billboard,
            approval_status=validated_data.get('approval_status', 'PENDING'),
            reject_reason=validated_data.get('reject_reason',None),
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude'),
            comment=validated_data.get('comment'),
            status=validated_data.get('status'),
            left=validated_data.get('left', None),
            front=validated_data.get('front', None),
            close=validated_data.get('close', None),
            right=validated_data.get('right', None),
        )

        # Save extra images
        if extra_images:
            for img in extra_images:
                extra_image_obj = TaskSubmissionExtraImages.objects.create(
                    task_submission=task_submission,
                    image=img
                )
                task_submission.extra_images.add(extra_image_obj)

        return task_submission

class CardDataSerializer(serializers.Serializer):
    visited = serializers.IntegerField()
    billboards = serializers.IntegerField()
    Good = serializers.IntegerField()
    Bad = serializers.IntegerField()

           
class CampaignSerializer(serializers.ModelSerializer):
    billboards = BillboardSerializer(many=True, required=False)
    
    
    user = UserSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    monitoring_requests = serializers.UUIDField(source='monitoring_request.uuid', required=False)  # Accept UUID of the billboard, but do not allow changes to it
    monitoring_requests = serializers.ListField(
        child=serializers.UUIDField(),
         write_only=True,required=False
    )
    all_monitorings = serializers.SerializerMethodField(read_only=True)
    # no billboard, billboard visited,
    card_data= serializers.SerializerMethodField()
    billboards = CustomBillboardSerializer(many=True, read_only=True)
    billboard_uuids = serializers.CharField(
        write_only=True,
        required=False,
        help_text="List of Billboard UUIDs to attach to the campaign",
    )

    

    class Meta:
        model = Campaign
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
        }
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['billboards'] = CustomBillboardSerializer(instance.billboards.all(), many=True).data
        data['total_visited'] = instance.monitoring_requests.filter(is_accepeted='ACCEPTED').distinct().count()
        bilboard_visited =[]
        for billboard in instance.billboards.all():
            visited = TaskSubmissionRequest.objects.filter(billboards=billboard,is_accepeted='ACCEPTED',campaign=instance).distinct().count()
            bilboard_visited.append({'billboard':billboard.uuid,'visited':visited})
        data['bilboard_visisted'] = bilboard_visited
        return data

    def get_billboards(self, obj):
        return  obj.billboards.all().values_list('uuid', flat=True)
    @extend_schema_field(CardDataSerializer)
    def get_card_data(self, obj):
        task_requests = TaskSubmissionRequest.objects.filter(
            campaign=obj,
        )
        task_req= task_requests.filter(is_accepeted='ACCEPTED',campaign=obj)
        max_visit_per_billboard = defaultdict(int)
        for req in task_req:
            billboard_id = req.billboards_id
            visit_number = getattr(req, 'visit_number', 1)
            if visit_number > max_visit_per_billboard[billboard_id]:
                max_visit_per_billboard[billboard_id] = visit_number
        visited = len(max_visit_per_billboard)
        good = 0
        allviews = obj.billboards.all().count()
        for billboard in obj.billboards.all():
            if billboard.views.exclude(status__in=['Good', 'Resolved']).exists():
                good += 1
        billboards = obj.billboards.all().count()
        return {'visited': visited, 'billboards': billboards, 'Good':  allviews - good, 'Bad':good}


    @extend_schema_field(TaskSubmissionSerializer(many=True))
    def get_all_monitorings(self, obj):
        task =TaskSubmissionRequest.objects.filter(
            campaign=obj,
        )
        
        tasks = [ task for task in task if task.task_list.exists()]
        senddata = []
        for tasksubmission in tasks:
            alltask = tasksubmission.task_list.all()
            for task in alltask:
                task = TaskSubmissionSerializer(task).data
                task['view'] = tasksubmission.view.id if tasksubmission.view else None
                senddata.append(task)
        
        return senddata

    def create(self, validated_data):
        billboards_data = validated_data.pop('billboard_uuids', [])
        billboards_data = billboards_data.split(',')
        print(billboards_data)
        campaign = Campaign.objects.create(**validated_data)
        for billboard_data in billboards_data:
            billboard = Billboard.objects.filter(uuid=billboard_data).first()
            if not billboard:
                raise serializers.ValidationError(f"Billboard with UUID {billboard_data} not found")
            monitoring_request = TaskSubmissionRequest.objects.create(
                user=validated_data.get('user'),
                billboards=billboard,
                campaign=campaign,
            )
            campaign.billboards.add(billboard)
            campaign.monitoring_requests.add(monitoring_request)
            
        return campaign
    def update(self, instance, validated_data):
        billboards_data = validated_data.pop('billboards', [])
        instance.user = validated_data.get('user', instance.user)
        instance.title = validated_data.get('title', instance.title)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        monitoring_requests_data = validated_data.pop('monitoring_requests', [])
        instance.monitor_time = validated_data.get('monitor_time', instance.monitor_time)
        instance.start_at = validated_data.get('start_at', instance.start_at)
        instance.end_at = validated_data.get('end_at', instance.end_at)
        instance.save()

        # Update billboards
        for billboard_data in billboards_data:
            billboard = Billboard.objects.get_object_or_404(uuid=billboard_data)
            instance.billboards.add(billboard)
        for monitoring_request_data in monitoring_requests_data:
            monitoring_request = TaskSubmissionRequest.objects.create(**monitoring_request_data)
            instance.monitoring_requests.add(monitoring_request)

        return instance

class TaskSubmissionRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    user_detail = UserSerializer(read_only=True)
    billboards = serializers.PrimaryKeyRelatedField(queryset=Billboard.objects.all(), write_only=True)
    billboard_detail = serializers.SerializerMethodField(read_only=True)
    stuff = serializers.UUIDField(source='stuff.uuid', write_only=True)  
    stuff_detail = StuffSerializer(read_only=True)
    task_list = TaskSubmissionSerializer(many=True, read_only=True)
    class Meta:
        model = TaskSubmissionRequest
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
            'billboards': {'required': False},
     

        }


    @extend_schema_field(CustomBillboardSerializer)
    def get_billboard_detail(self, obj):
        billboard = obj.billboards 
        return CustomBillboardSerializer(billboard).data

    def create(self, validated_data):
        user = validated_data.pop('user', None)
        billboard = validated_data.pop('billboards', None)
        monitoring = TaskSubmissionRequest.objects.create(user=user, billboard=billboard,is_accepeted='PENDING', **validated_data)
        return monitoring

    def update(self, instance, validated_data):
       
        instance.user = validated_data.get('user', instance.user)
        new_status = validated_data.get('is_accepeted', instance.is_accepeted)
        stuff = validated_data.get('stuff', None)
        if stuff is not None:
            instance.stuff = Stuff.objects.get_object_or_404(uuid=validated_data.get('stuff', instance.stuff))

        # Use the correct field name and get the Billboard instance
        billboard_obj = validated_data.get('billboards', instance.billboards)

        if instance.is_accepeted != new_status and new_status == 'ACCEPTED':
            campaign = Campaign.objects.filter(
                uuid=instance.campaign.uuid
            ).first()
            if not campaign:
                raise serializers.ValidationError("Campaign not found for this billboard")
            # Convert monitor_time to int safely
            
            monitor_time = int(campaign.monitor_time)
            print(CampaignSerializer(campaign).data)
            

            for i in range(monitor_time):
                task = TaskSubmission.objects.create(
                    user=instance.user,
                    billboard=billboard_obj,
                    visit_number=i+1,
                )
                instance.task_list.add(task)

        instance.is_accepeted = new_status
        if 'billboards' in validated_data:
            instance.billboards = validated_data['billboards']
        instance.save()
        return instance
    
    
class GpsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gps
        fields = '__all__'

class CvSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cv
        fields = '__all__'

class Cv_countSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cv_count
        fields = '__all__'

class PoiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poi
        fields = '__all__'

class WithdrawalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Withdrawal
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(source='user.id', read_only=True)
    class Meta:
        model = Notification
        fields = '__all__'






