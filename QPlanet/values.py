# Global values

ERROR = 0
ACCEPT = 1
FORM_ERROR = r"参数格式错误，请检查传参"

SAVED = 0
RELEASE = 1
DELETED = 2

SINGLE_CHOICE = 0		# 单选
MULTIPLE_CHOICE = 1		# 多选
COMPLETION = 2			# 填空
DESCRIPTION = 3			# 问答
GRADING = 4				# 打分
LOCATION = 5			# 定位

SEPARATOR = "Y@7$"

NORMAL = 0				# 普通问卷
VOTING_BEFORE = 1		# 投票问卷(填写前给数据)
VOTING_AFTER = 2		# 投票问卷(填写后给数据)
VOTING_BOTH = 3			# 投票问卷(都给)
VOTING_NO = 4			# 投票问卷(都不给)
SIGNUP = 5				# 报名问卷
TESTING_SCORE = 6		# 考试问卷(给分数)
TESTING_CORRECTION = 7	# 考试问卷(给答案)
TESTING_BOTH = 8		# 考试问卷(都给)
TESTING_NO = 9			# 考试问卷(都不给)

NO_CERTIFICATION = 0
EMAIL_CERTIFICATION = 1
WEAK_CERTIFICATION = 2
STRONG_CERTIFICATION = 3

NO_REQUIREMENT = 0		# 无检测
PHONE_NUM = 1			# 手机号检测
EMAIL_ADRESS = 2		# 邮箱检测
NUMBER_ONLY = 3			# 纯数字检测

RESERVE_RESULTS = 0	
DELETE_RESULTS = 1