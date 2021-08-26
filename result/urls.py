from django.urls import path
from result.views import *

urlpatterns = [
	path('send_captcha/',send_captcha),
	path('check_captcha/',check_captcha),
	path('submit/', submit),
	path('analyze/', analyze),
	path('download/', download),
]