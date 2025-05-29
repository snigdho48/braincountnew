import uuid
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from api.services.constants import *
from django.utils import timezone
from multiselectfield import MultiSelectField


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
    title = models.CharField(max_length=255,null=True, blank=True)
    location = models.ForeignKey('Location', on_delete=models.DO_NOTHING,related_name='billboards',null=True, blank=True)


    faces = models.CharField(choices=BILLBORD_FACES, max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.ManyToManyField('Billboard_View', related_name='billboards',blank=True,null=True)

    def __str__(self):
        return self.title 
    
class Billboard_View(models.Model):
    camera_id = models.CharField(max_length=255,null=True, blank=True)
    front = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    left = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    right = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    close = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    billboard_type = models.CharField(choices=BILLBORD_TYPES, max_length=200)
    category = models.CharField(choices=BILLBORD_CATEGORY, max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=BILLBOARD_STATUS,null=True, blank=True)
    details = models.ForeignKey('Billboard_info', on_delete=models.DO_NOTHING,related_name='billboards',null=True, blank=True)


    
    def __str__(self):
        return str(self.pk) + " - " + self.billboard_type 
    


   
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
    status =   MultiSelectField(choices=BILLBOARD_STATUS, max_length=100, null=True, blank=True)
    billboard = models.ForeignKey('Billboard', on_delete=models.DO_NOTHING,related_name='monitoring',null=True, blank=True)
    front = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    left = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    right = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    close = models.ImageField(upload_to='billboard_images/',null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,editable=True)
    updated_at = models.DateTimeField(default=timezone.now)
    extra_images = models.ManyToManyField('TaskSubmissionExtraImages', related_name='task_submissions', blank=True)
    approval_status = models.CharField(choices=APPROVAL_STATUS, max_length=20,null=True, blank=True)
    reject_reason = models.TextField(null=True, blank=True)
    

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
    view = models.ForeignKey('Billboard_View', on_delete=models.DO_NOTHING,related_name='monitoring_requests',null=True, blank=True)
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
        
class TaskSubmissionExtraImages(models.Model):
    task_submission = models.ForeignKey('TaskSubmission', on_delete=models.CASCADE,related_name='extra_images_task_submission')
    image = models.ImageField(upload_to='billboard_images/monitoring_extra/',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.image.name + " - " + str(self.task_submission.uuid))
    
class Location(models.Model):
    country = models.CharField(max_length=255,null=True, blank=True)
    division = models.CharField(max_length=255,null=True, blank=True)
    district = models.CharField(max_length=255,null=True, blank=True)
    thana = models.CharField(max_length=255,null=True, blank=True)
    town_class = models.CharField(max_length=255,null=True, blank=True)
    location = models.CharField(max_length=255,null=True, blank=True)
    extrapolation_factor = models.FloatField(null=True, blank=True,default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.location
    
class Billboard_info(models.Model):
    height_from_ground_m = models.FloatField(null=True, blank=True)
    panel_height_ft = models.FloatField(null=True, blank=True)
    panel_width_ft = models.FloatField(null=True, blank=True)
    angle = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    location_type = models.CharField(choices=LOCATION_TYPE, max_length=200, null=True, blank=True)
    traffic_direction = models.CharField(choices=TRAFFIC_DIRECTION, max_length=200, null=True, blank=True)
    has_obstruction = models.BooleanField(default=False)
    facing = models.TextField(null=True, blank=True)
    obstruction_details = models.TextField(null=True, blank=True)
    angle_to_road_dg = models.FloatField(null=True, blank=True)
    road_bearing_dg = models.FloatField(null=True, blank=True)
    road_width_m = models.FloatField(null=True, blank=True)
    is_parallel_to_road = models.BooleanField(default=False)
    elevation = models.FloatField(null=True, blank=True)
    structure_type = models.CharField(choices=STRUCTURE_TYPE, max_length=200, null=True, blank=True)
    screen_resolution = models.CharField( max_length=20, null=True, blank=True)
    has_sound = models.BooleanField(default=False)
    has_night_light = models.BooleanField(default=False)
    has_spot_light = models.BooleanField(default=False)
    has_back_lit = models.BooleanField(default=False)
    opt_hours = models.TextField(null=True, blank=True)
    distance_of_closest_neighbour_m = models.FloatField(null=True, blank=True)
    total_neighbours = models.IntegerField(null=True, blank=True)
    observation_zone  = models.TextField(null=True, blank=True)
    visible_zone  = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return str(self.pk)
    
class Poi(models.Model):
    name = models.CharField(max_length=255,null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    primary_type = models.CharField(choices=POI_TYPE, max_length=200, null=True, blank=True)
    types = MultiSelectField(choices=POI_TYPE, max_length=250, null=True, blank=True)
    google_mal_url = models.TextField(null=True, blank=True)
    bc_category = models.CharField(choices=BC_CATEGORY, max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='poi_created_by',null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='poi_updated_by',null=True, blank=True)
    bc_sub_category = models.CharField(choices=POI_TYPE, max_length=200, null=True, blank=True)
    source = models.CharField( max_length=200, null=True, blank=True)
    status = models.CharField(choices=POI_STATUS, max_length=200, null=True, blank=True)
    
    
    def __str__(self):
        return self.name
    
class Cv_count(models.Model):
    object_type = models.CharField(max_length=255,null=True, blank=True,choices=OBJECT_TYPE)
    week_day = models.CharField(max_length=50,null=True, blank=True,choices=WEEK_DAY)
    hour = models.IntegerField(null=True, blank=True)
    passenger = models.IntegerField(null=True, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=255,null=True, blank=True,choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='cv_count_created_by',null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='cv_count_updated_by',null=True, blank=True)
    
    def __str__(self):
        return str(self.object_type + " - " + str(self.week_day) + " - " + str(self.hour))
    
class Gps(models.Model):
    billboard = models.ForeignKey('Billboard', on_delete=models.DO_NOTHING,related_name='gps')
    view = models.ForeignKey('Billboard_View', on_delete=models.DO_NOTHING,related_name='gps',null=True, blank=True)
    location = models.ForeignKey('Location', on_delete=models.DO_NOTHING,related_name='gps',null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    hour = models.IntegerField(null=True, blank=True)
    ots = models.IntegerField(null=True, blank=True)
    lts = models.IntegerField(null=True, blank=True)
    reach = models.IntegerField(null=True, blank=True)
    dwell_time = models.FloatField(null=True, blank=True)
    device_ids= models.TextField(null=True, blank=True)
    ips = models.TextField(null=True, blank=True)
    extrapolated_ots = models.IntegerField(null=True, blank=True)
    extrapolated_lts = models.IntegerField(null=True, blank=True)
    extrapolated_reach = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return str(self.billboard.title + " - " + str(self.date) + " - " + str(self.hour))
    
class Cv(models.Model):
    camera_id = models.CharField(max_length=255,null=True, blank=True)
    billboard = models.ForeignKey('Billboard', on_delete=models.DO_NOTHING,related_name='cvs')
    view = models.ForeignKey('Billboard_View', on_delete=models.DO_NOTHING,related_name='cvs',null=True, blank=True)
    object_type = models.CharField(max_length=255,null=True, blank=True,choices=OBJECT_TYPE)
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    dwell_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.camera_id + " - " + str(self.billboard.title))
    
class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='withdrawals')
    amount = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=255,null=True, blank=True,choices=APPROVAL_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user.username + " - " + str(self.amount))

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.message[:30]}"