from django.urls import path
from questionnaire.views import *

urlpatterns = [
	path('create/', create),
	path('list/', list),
	path('reset/', reset_hash),
	path('delete/', delete),
	path('recover/', recover),
	path('release/', release),
	path('close/', close),
	#path('sorted/', get_sorted_questionnaires),
	path('search/', search_questionnaires),
	path('view/', view),
	path('modify/', modify_questionnaire),
	path('copy/', copy_questionnaire_to_self),
	path('getqr/', get_qr),
	path('download/', download),
	path('fill/', fill),
	path('check_type/', check_type),
	path('get_total/', get_total),
	path('savelogic/', save_logic),
]