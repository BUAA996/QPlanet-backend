from django.urls import path
from question.views import *

urlpatterns = [
	path('surplus/', surplus_quota)
]