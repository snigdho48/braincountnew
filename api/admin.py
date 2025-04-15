from django.contrib import admin


admin.site.site_header = "BrainCount Admin"
admin.site.site_title = "BrainCount Admin Portal"
admin.site.index_title = "Welcome to BrainCount Admin Portal"

from api.models import *

admin.site.register(Monitor)
admin.site.register(Billboard)
admin.site.register(TaskSubmission)
admin.site.register(Campaign)
admin.site.register(TaskSubmissionRequest)

# Register your models here.
