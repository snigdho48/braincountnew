

from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# from rest_framework_simplejwt.views import TokenRefreshView
from .views import *


apidoc_urlpatterns = [
  path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('test/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


urlpatterns = [
  path('auth/login/', LoginApiView.as_view(), name='login'),
  path('auth/logout/', LogoutApiView.as_view(), name='logout'),
  path('monitoring/', MonitoringView.as_view(), name='monitoring'),
  path('monitoring/billboard-status/', BillboardStatusView.as_view(), name='billboard-status'),
  path('campaign/', CampaignApiView.as_view(), name='campaign'),
  path('billboard/', BillboardApiView.as_view(), name='billboard'),
  path('monitoring-request/', MonitoringRequestApiView.as_view(), name='monitoring-request'),
  
  
    
]+ apidoc_urlpatterns
