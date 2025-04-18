import uuid
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from api.services.constants import *
from django.utils import timezone


class Monitor(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = PhoneNumberField(region='BD', unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Stuff(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = PhoneNumberField(region='BD', unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username

class Advertiser(models.Model):
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
    faces = models.CharField(choices=BILLBORD_FACES, max_length=200, null=True, blank=True)
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
    type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.title
    

class TaskSubmission(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True,editable=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.uuid)
    def save(self, *args, **kwargs):
        if self.pk:
            # Fetch current value from DB
            old = TaskSubmissionRequest.objects.filter(pk=self.pk).only('updated_at').first()
            if old and self.updated_at == old.updated_at:
                # Only update if the field hasn't been manually modified
                self.updated_at = timezone.now()
        else:
            # On create, always set it
            self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)
    
class TaskSubmissionRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='monitoring_requests')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    billboards = models.ForeignKey('Billboard', on_delete=models.DO_NOTHING,related_name='monitoring_requests',null=True, blank=True)
    is_accepeted = models.CharField(choices=TASK_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True,editable=True)
    updated_at = models.DateTimeField(default=timezone.now)
    campaign = models.ForeignKey('Campaign', on_delete=models.DO_NOTHING,related_name='monitoring_requests')
    task_list = models.ManyToManyField('TaskSubmission', related_name='monitoring_requests', blank=True)
    stuff = models.ForeignKey('Stuff', on_delete=models.DO_NOTHING,related_name='monitoring_requests',null=True, blank=True)
    def __str__(self):
        return str(self.uuid)
    def save(self, *args, **kwargs):
        if self.pk:
            # Fetch current value from DB
            old = TaskSubmissionRequest.objects.filter(pk=self.pk).only('updated_at').first()
            if old and self.updated_at == old.updated_at:
                # Only update if the field hasn't been manually modified
                self.updated_at = timezone.now()
        else:
            # On create, always set it
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)
