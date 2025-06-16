

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
  # auth
  path('auth/login/', LoginApiView.as_view(), name='login'),
  path('auth/logout/', LogoutApiView.as_view(), name='logout'),
  # monitoring
  path('monitoring/', MonitoringView.as_view(), name='monitoring'),
  path('monitoring/billboard-status/', BillboardStatusView.as_view(), name='billboard-status'),
  # campaign
  path('campaign/', CampaignApiView.as_view(), name='campaign'),
  path('billboard/', BillboardApiView.as_view(), name='billboard'),
  path('location/', LocationApiView.as_view(), name='location'),
  path('billboard_info/', BillboardInfoApiView.as_view(), name='billboard-info'),
  
  path('poi/', PoiApiView.as_view(), name='poi'),
  path('cv_count/', CvCountApiView.as_view(), name='cv-count'),
  path('gps/', GpsApiView.as_view(), name='gps'),
  path('cv/', CvApiView.as_view(), name='cv'),
  path('billboard_view/', BillboardViewApiView.as_view(), name='billboard-view'),
  path('monitoring_request/', MonitoringRequestApiView.as_view(), name='monitoring-request'),
  path('monitoring_request/status', MonitoringRequestStatus.as_view(), name='monitoring-request-status'),
  path('withdraw/', WithdrawalApiView.as_view(), name='withdraw'),
  path('report/', CalculateReportView.as_view(), name='report'),
  path('report/upload/', UploadReportView.as_view(), name='report-upload'),
  path('report/delete/', ImpreessionDetailView.as_view(), name='impression-detail'),
    
]+ apidoc_urlpatterns 
