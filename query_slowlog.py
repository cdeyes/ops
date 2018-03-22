# -*- coding: utf-8 -*-
from aliyunsdkcore.client import AcsClient
from aliyunsdkrds.request.v20140815 import DescribeSlowLogsRequest
from datetime import date, timedelta
import json
import csv
import os
from txfunctions import smail

ISOTIMEFORMAT = '%Y-%m-%dZ'
Log_Date = (date.today() - timedelta(days=1)).strftime(ISOTIMEFORMAT)
client = AcsClient('XXXXXXX', 'XXXXXXXXXX', 'cn-beijing')
request = DescribeSlowLogsRequest.DescribeSlowLogsRequest()
request.set_DBInstanceId('XXXXX')
request.set_accept_format('json')
request.set_PageSize(100)
request.set_StartTime(Log_Date)
request.set_EndTime(Log_Date)
response = client.do_action_with_exception(request)
messages = json.loads(response).get('Items').get('SQLSlowLog')
SlowFlag = 2
csv_file_name = '/tmp/Cse_SlowLOg_' + Log_Date + '.csv'
mail_addrs = ["XXXXX", "XXXX"]
mail_body = u'阿里云RDS慢查询日志,详情见附件。'
mail_subject = u'阿里云RDS慢查询日志-' + Log_Date
mail_attachments = [csv_file_name]
if messages:
	SlowFlag = 1
	headers = messages[0].keys()
	with open(csv_file_name, 'wb') as csvfile:
		csv_writer = csv.DictWriter(csvfile, headers)
		csv_writer.writeheader()
		for item in messages:
			csv_writer.writerow(item)

if SlowFlag == 1:
	smail(mail_addrs, mail_body, mail_subject, mail_attachments)