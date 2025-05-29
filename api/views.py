from django.shortcuts import render

from api.services.auth import LoginApiView, LogoutApiView
from api.services.monitoring import BillboardStatusView, MonitoringView
from api.services.campaign import CampaignApiView
from api.services.billboard import BillboardApiView
from api.services.monitoring_requset import MonitoringRequestApiView, MonitoringRequestStatus
from api.services.location import LocationApiView
from api.services.billboard_info import BillboardInfoApiView
from api.services.poi import PoiApiView
from api.services.cv_count import CvCountApiView
from api.services.gps import GpsApiView
from api.services.cv import CvApiView
from api.services.billboard_view import BillboardViewApiView
from api.services.withdraw import WithdrawalApiView

