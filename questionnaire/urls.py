from django.urls import path
from questionnaire.views import *

urlpatterns = [
	path('create/', create),
	path('list/', list),
	path('reset/', reset_hash),
	path('delete/', delete),
	path('recover/', recover),
]