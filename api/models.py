import uuid
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from api.services.constants import *


class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = PhoneNumberField(region='BD', unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Billboard(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BILLBOARD_STATUS,null=True, blank=True)
    title = models.CharField(max_length=255,null=True, blank=True)
    location = models.CharField(max_length=255,null=True, blank=True)
    front = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    left = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    right = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    close = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    billboard_type = models.CharField(choices=BILLBORD_TYPES, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title 

   
class Campaign(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    billboards = models.ManyToManyField('Billboard', related_name='campaigns',blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='campaigns')
    title = models.CharField(max_length=255,null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    monitor_time = models.CharField(max_length=20, choices=MONITOR_TIME, null=True, blank=True)
    start_at = models.TimeField(null=True, blank=True)
    end_at = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.title
    

class Monitoring(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='monitoring')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BILLBOARD_STATUS,null=True, blank=True)
    billboard = models.ForeignKey('Billboard', on_delete=models.DO_NOTHING,related_name='monitoring')
    front = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    left = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    right = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    close = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.uuid)
    
class MonitoringRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='monitoring_requests')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    billboards = models.ForeignKey('Billboard', on_delete=models.DO_NOTHING,related_name='monitoring_requests',null=True, blank=True)
    is_accepeted = models.CharField(choices=TASK_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey('Campaign', on_delete=models.DO_NOTHING,related_name='monitoring_requests')

    def __str__(self):
        return str(self.uuid)