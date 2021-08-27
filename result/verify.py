from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.auth.credentials import StsTokenCredential
from QPlanet.settings import *
from random import randint as rand

def send_code(phone):
	# TODO check phone
	credentials = AccessKeyCredential(KEY_ID, KEY_SECRET)
	# use STS Token
	# credentials = StsTokenCredential('<your-access-key-id>', '<your-access-key-secret>', '<your-sts-token>')
	client = AcsClient(region_id='cn-beijing', credential=credentials)

	request = CommonRequest()
	request.set_accept_format('json')
	request.set_domain('dysmsapi.aliyuncs.com')
	request.set_method('POST')
	request.set_protocol_type('https') # https | http
	request.set_version('2017-05-25')
	request.set_action_name('SendSms')

	request.add_query_param('PhoneNumbers', phone)
	request.add_query_param('SignName', "问卷星球")
	request.add_query_param('TemplateCode', "SMS_222870677")
	
	number = str(rand(100000,999999))
	request.add_query_param('TemplateParam', "{\"code\": " + number + "}")

	response = client.do_action(request)
	return number