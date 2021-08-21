from django.urls import path
from questionnaire.views import *

urlpatterns = [
	path('create/', create),
]