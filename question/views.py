from django.shortcuts import render
from question.models import *
from django.views.decorators.csrf import csrf_exempt
from QPlanet.values import *
from QPlanet.settings import *
#from questionnaire.views import *
# Create your views here.

@csrf_exempt
def save_questions(questions, qid):
    if questions:
        num = 1
        for x in questions:
            question = Question(
                questionnaire_id = qid, rank = num, type = x['type'], content = x['content'], 
                is_required = x['is_required']
            )
            if x['type'] == SINGLE_CHOICE or MULTIPLE_CHOICE:
                question.option = x['option']
            question.save()
            num += 1
