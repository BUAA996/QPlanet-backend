from django.shortcuts import render
from question.models import *
from django.views.decorators.csrf import csrf_exempt
from QPlanet.values import *
from QPlanet.settings import *
#from questionnaire.views import *
# Create your views here.

def list_to_string(option):
    return SEPARATOR.join(option)

def string_to_list(option):
    return option.split(SEPARATOR)

def save_questions(questions, qid):
    if questions:
        num = 1
        for x in questions:
            question = Question(
                questionnaire_id = qid, rank = num, type = x['type'], content = x['content'], 
                is_required = x['is_required'], description = x['description']
            )
            if x['type'] == SINGLE_CHOICE or x['type'] == MULTIPLE_CHOICE:
                question.option = list_to_string(x['option'])
            question.save()
            num += 1

def delete_question(qid):
    Question.objects.filter(questionnaire_id = qid).delete()

def get_questions(qid):
    questions = [x for x in Question.objects.filter(questionnaire_id = qid)]
    questions.sort(key = lambda x: x.rank)
    tmp = []
    for x in questions:
        if x.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]: 
            d = {'id':x.id, 'type':x.type, 'content':x.content, 'option':string_to_list(x.option),
                'is_required':x.is_required, 'description':x.description }
        else:
            d = {'id':x.id, 'type':x.type, 'content':x.content, 'is_required':x.is_required,
                'description':x.description }
        tmp.append(d)
    return tmp

def get_questions_without_id(qid):
    questions = [x for x in Question.objects.filter(questionnaire_id = qid)]
    questions.sort(key = lambda x: x.rank)
    tmp = []
    for x in questions:
        if x.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]: 
            d = {'type':x.type, 'content':x.content, 'option':string_to_list(x.option),
                'is_required':x.is_required, 'description':x.description }
        else:
            d = {'type':x.type, 'content':x.content, 'is_required':x.is_required,
                'description':x.description }
        tmp.append(d)
    return tmp

def update_questions(questions):
    num = 1
    for x in questions:
        question = Question.objects.get(id = x['id'])
        question.content= x['content']
        question.is_required = x['is_required']
        question.description = x['description']
        question.rank = num
        if type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
            question.option = list_to_string(x['option'])
        question.save()
        num += 1