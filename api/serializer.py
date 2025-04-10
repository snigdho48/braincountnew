from rest_framework import serializers
from django.contrib.auth.models import User,Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.shortcuts import get_object_or_404



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
    group = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'group', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'groups': {'required': False},
        }

    # Custom method to return only the first group
    def get_groups(self, obj):
        # Return only the first group or None if no groups exist
        if obj.groups.exists():
            return  obj.groups.first().name
        return []


class MonitoringSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(source='user.id', write_only=True)  # Accept user ID, but do not allow changes to it
    billboard = serializers.UUIDField(source='billboard.uuid', required=False)  # Accept UUID of the billboard, but do not allow changes to it
    class Meta:
        model = Monitoring
        fields = ['user_id', 'uuid', 'latitude', 'longitude', 'status', 'billboard','billboard_type', 'front', 'left', 'right', 'close', 'comment', 'created_at', 'updated_at','user']
    def update(self, instance, validated_data):
        # Don't allow changes to the billboard
        # if logined user is not admin
        if  instance.user.groups.filter(name='admin').exists():
            instance.billboard = validated_data.get('billboard', instance.billboard)
            instance.user = validated_data.get('user', validated_data['user_id'])
        validated_data.pop('billboard', None) 
        if not (instance.front and instance.left and instance.right and instance.close):
            raise serializers.ValidationError("Please upload Images")
        if instance.status is None:
            raise serializers.ValidationError("Please select status")
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.status = validated_data.get('status', instance.status)
        instance.front = validated_data.get('front', instance.front)
        instance.left = validated_data.get('left', instance.left)
        instance.right = validated_data.get('right', instance.right)
        instance.close = validated_data.get('close', instance.close)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()

        return instance

        
class BillboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billboard
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
        }
        
class CampaignSerializer(serializers.ModelSerializer):
    billboards = BillboardSerializer(many=True, required=False)
    user = UserSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    billboard = serializers.UUIDField(source='billboard.uuid', required=False)  # Accept UUID of the billboard, but do not allow changes to it
    monitoring_requests = serializers.UUIDField(source='monitoring_request.uuid', required=False)  # Accept UUID of the billboard, but do not allow changes to it
    monitoring_requests = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )
    
    class Meta:
        model = Campaign
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
            'billboard': {'required': False},
        }
    def create(self, validated_data):
        billboards_data = validated_data.pop('billboards', [])
        campaign = Campaign.objects.create(**validated_data)
        for billboard_data in billboards_data:
            billboard = Billboard.objects.get_object_or_404(uuid=billboard_data)
            monitoring_request = MonitoringRequest.objects.create(
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
            monitoring_request = MonitoringRequest.objects.create(**monitoring_request_data)
            instance.monitoring_requests.add(monitoring_request)

        return instance
class CustomBillboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billboard
        fields = ['uuid',  'status', 'title', 'location', 'billboard_type']
class MonitoringRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    billboards = CustomBillboardSerializer(many=True, required=False)
    billboards = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )
    class Meta:
        model = Monitoring
        fields = '__all__'

    def create(self, validated_data):
        billboards_data = validated_data.pop('billboards', [])
        monitoring = Monitoring.objects.create(**validated_data)
        for billboard_data in billboards_data:
            billboard = Billboard.objects.get_object_or_404(uuid=billboard_data)
            monitoring.billboards.add(billboard)
        return monitoring
    def update(self, instance, validated_data):
        billboards_data = validated_data.pop('billboards', [])
        instance.user = validated_data.get('user', instance.user)
        instance.is_accepted = validated_data.get('is_accepted', instance.is_accepted)
        

        # Update billboards
        for billboard_data in billboards_data:
            billboard = Billboard.objects.get_object_or_404(uuid=billboard_data)
            instance.billboards.add(billboard)


        return instance