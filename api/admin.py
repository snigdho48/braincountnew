from django.contrib import admin


admin.site.site_header = "BrainCount Admin"
admin.site.site_title = "BrainCount Admin Portal"
admin.site.index_title = "Welcome to BrainCount Admin Portal"

from api.models import *

admin.site.register(Supervisor)
admin.site.register(Billboard)
admin.site.register(Monitoring)

# Register your models here.
