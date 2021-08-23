from django.urls import path
from user.views import *

urlpatterns = [
	path('register/', register),
	path('login/', login),
	path('logout/', logout),
	path('getcode/', send_code),
	path('captcha/', get_captcha),
	path('islogin/', is_login), 
	path('info/', info),
	path('change/', change_password),
]