from django.urls import path
from result.views import *

urlpatterns = [
	path('submit/', submit),
	path('analyze/', analyze),
]