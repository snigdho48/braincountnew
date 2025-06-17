from django.contrib import admin

admin.site.site_header = "BrainCount Admin Dashboard"
admin.site.site_title = "BrainCount Admin Portal"
admin.site.index_title = "Welcome to BrainCount Admin Portal"

from api.models import *

admin.site.register(Monitor)
admin.site.register(Billboard)
admin.site.register(TaskSubmission)
admin.site.register(Campaign)
admin.site.register(TaskSubmissionRequest)
admin.site.register(TaskSubmissionExtraImages)
admin.site.register(Location)
admin.site.register(Billboard_info)
admin.site.register(Cv_count)
admin.site.register(Cv)
admin.site.register(Poi)
admin.site.register(Gps)
admin.site.register(Billboard_View)
admin.site.register(Withdrawal)
admin.site.register(Withdrawal_Task_Amount)
admin.site.register(Notification)
admin.site.register(Campaign_Time)
admin.site.register(Impression)
admin.site.register(Impression_Detail)
admin.site.register(Impression_Reach_Id)
# Register your models here.
