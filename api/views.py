from django.shortcuts import render

from api.services.auth import LoginApiView, LogoutApiView
from api.services.monitoring import BillboardStatusView, MonitoringView
from api.services.campaign import CampaignApiView
from api.services.billboard import BillboardApiView
from api.services.monitoring_requset import MonitoringRequestApiView, MonitoringRequestStatus

