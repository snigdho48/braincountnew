import uuid
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField



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
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    front = models.ImageField(upload_to='billboard_images/')
    left = models.ImageField(upload_to='billboard_images/')
    right = models.ImageField(upload_to='billboard_images/')
    close = models.ImageField(upload_to='billboard_images/')
    billboard_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    
    
BILLBOARD_STATUS = (
    ('Good', 'Good'),
    ('Broken', 'Broken'),
    ('Under Maintenance', 'Under Maintenance'),
    ('Not Working', 'Not Working'),
    ('Not Clear', 'Not Clear'),
    ('Not Visible', 'Not Visible'),
    ('Other', 'Other'),
)

class Monitoring(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=BILLBOARD_STATUS)
    billboard = models.ForeignKey('Billboard', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username