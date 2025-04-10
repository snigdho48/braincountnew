from rest_framework import serializers
from django.contrib.auth.models import User,Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from uuid import UUID


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
        fields = ['user_id', 'uuid', 'latitude', 'longitude', 'status', 'billboard', 'front', 'left', 'right', 'close', 'comment', 'created_at', 'updated_at','user']
    def update(self, instance, validated_data):
        # Don't allow changes to the billboard
        # if logined user is not admin
        if  instance.user.groups.filter(name='admin').exists():
            instance.billboard = validated_data.get('billboard', instance.billboard)
            instance.user = validated_data.get('user', validated_data['user_id'])
        validated_data.pop('billboard', None) 
        # if not (instance.front and instance.left and instance.right and instance.close):
        #     raise serializers.ValidationError("Please upload Images")
        # if instance.status is None:
        #     raise serializers.ValidationError("Please select status")
            
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