from rest_framework import serializers
from django.contrib.auth.models import User,Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_field



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

class BillboardSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = TaskSubmission
        fields = ['user_id', 'uuid', 'latitude', 'longitude', 'status', 'billboard', 'front', 'left', 'right', 'close', 'comment', 'created_at', 'updated_at','user','billboard_detail','extra_images','extra_images_list']
        extra_kwargs = {
            'user': {'required': False},
            'billboard': {'required': False},
        }
    @extend_schema_field(BillboardSerializer)
    def get_billboard_detail(self, obj):
        return BillboardSerializer(obj.billboard).data
    
    @extend_schema_field(TaskSubmissionExtraImagesSerializerDisplay(many=True))
    def get_extra_images_list(self, obj):
        extra_images = obj.extra_images.all()
        return TaskSubmissionExtraImagesSerializerDisplay(extra_images, many=True).data
        
    
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

class CardDataSerializer(serializers.Serializer):
    visited = serializers.IntegerField()
    billboards = serializers.IntegerField()
    Good = serializers.IntegerField()
    Bad = serializers.IntegerField()

        
class CampaignSerializer(serializers.ModelSerializer):
    billboards = BillboardSerializer(many=True, required=False)
    user = UserSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    # monitoring_requests = serializers.UUIDField(source='monitoring_request.uuid', required=False)  # Accept UUID of the billboard, but do not allow changes to it
    monitoring_requests = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )
    all_monitorings = serializers.SerializerMethodField()
    # no billboard, billboard visited,
    card_data= serializers.SerializerMethodField()
    

    class Meta:
        model = Campaign
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
            'billboard': {'required': False},
        }
    @extend_schema_field(CardDataSerializer)
    def get_card_data(self, obj):
        task_requests =TaskSubmissionRequest.objects.filter(
            campaign=obj,
        )
        visited=0
        good =0
        for task_request in task_requests:
            print(task_request.billboards)
            if task_request.task_list.filter(status__isnull=False).exists():
                visited += 1
        for billboard in obj.billboards.all():
            if billboard.status== 'Good':
                good += 1

        billboards = obj.billboards.all().count()
        
        return {'visited':visited,'billboards':billboards,'Good':good,'Bad':billboards-good}
            

    @extend_schema_field(TaskSubmissionSerializer(many=True))
    def get_all_monitorings(self, obj):
        task =TaskSubmissionRequest.objects.filter(
            campaign=obj,
        )
        tasksubmission = [t for task in task for t in task.task_list.all()]
        return TaskSubmissionSerializer(tasksubmission, many=True).data

    def create(self, validated_data):
        billboards_data = validated_data.pop('billboards', [])
        campaign = Campaign.objects.create(**validated_data)
        for billboard_data in billboards_data:
            billboard = Billboard.objects.get_object_or_404(uuid=billboard_data)
            monitoring_request = TaskSubmissionRequest.objects.create(
                user=validated_data.get('user'),
                billboard=billboard,
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
class CustomBillboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billboard
        fields = ['uuid',  'status', 'title', 'location', 'billboard_type']
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
            'is_accepeted': {'required': False}

        }


    @extend_schema_field(CustomBillboardSerializer)
    def get_billboard_detail(self, obj):
        billboard = obj.billboards 
        return {
            'id':billboard.id,
            'uuid': billboard.uuid,
            'status': billboard.status,
            'title': billboard.title,
        }

    def create(self, validated_data):
        user = validated_data.pop('user', None)
        billboard = validated_data.pop('billboards', None)
        monitoring = TaskSubmissionRequest.objects.create(user=user, billboard=billboard, **validated_data)
        return monitoring

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        new_status = validated_data.get('is_accepeted', instance.is_accepeted)
        stuff =validated_data.get('stuff', None)
        if stuff is not None:
            instance.stuff = Stuff.objects.get_object_or_404(uuid=validated_data.get('stuff', instance.stuff))
            
            
        
        if instance.is_accepeted != new_status and new_status == 'ACCEPTED':
         
            campaign=Campaign.objects.filter(
                billboards=validated_data.get('billboard', instance.billboards),
                start_date__lte=instance.created_at,
                end_date__gte=instance.created_at,
                user=instance.user
            ).first()
            for monitoring in range(0,int(campaign.monitor_time)):
                
                task=TaskSubmission.objects.create(
                    user=instance.user,
                    billboard=validated_data.get('billboard', instance.billboards),
                )
                instance.task_list.add(task)


        instance.is_accepeted = new_status
        if 'billboard' in validated_data:
            instance.billboard = validated_data['billboard']
        instance.save()
        return instance
