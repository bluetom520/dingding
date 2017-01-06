#!/usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = '懒懒的天空'

import requests
import sys
import json
import logging
from conf.INIFILES import read_config, write_config
import os
import datetime
from conf.BLog import Log
reload(sys)
sys.setdefaultencoding('utf-8')


class Dingtalk(object):
    def __init__(self, corpid, corpsecret): # 初始化的时候需要获取corpid和corpsecret，需要从管理后台获取
        self.__params = {
            'corpid': corpid,
            'corpsecret': corpsecret
        }

        self.url_get_token = 'https://oapi.dingtalk.com/gettoken'
        self.url_get_dept_list = 'https://oapi.dingtalk.com/department/list'
        self.url_get_dept_detail = 'https://oapi.dingtalk.com/department/get'
        self.url_create_dept = 'https://oapi.dingtalk.com/department/create'
        self.url_delete_dept = 'https://oapi.dingtalk.com/department/delete'
        self.url_get_user_id_by_unionid = 'https://oapi.dingtalk.com/user/getUseridByUnionid'
        self.url_get_user_detail = 'https://oapi.dingtalk.com/user/get'
        self.url_send_message = 'https://oapi.dingtalk.com/message/send_to_conversation'
        self.url_send = 'https://oapi.dingtalk.com/message/send'
        self.url_get_user_count = 'https://oapi.dingtalk.com/user/get_org_user_count'
        self.__token = self.__get_token()
        self.__token_params = {
            'access_token': self.__token
        }

    def __raise_error(self, res):
        raise Exception('error code: %s,error message: %s' % (res.json()['errcode'], res.json()['errmsg']))
        global senderr
        sendstatus = False
        senderr = 'error code: %s,error message: %s' % (res.json()['errcode'], res.json()['errmsg'])

    def __get_token(self):
        # print self.url_get_token
        headers = {'content-type': 'application/json'}
        res = requests.get(self.url_get_token, headers=headers,  params=self.__params)

        try:
            return res.json()['access_token']
        except:
            self.__raise_error(res.content)

    def get_dept_list(self):
        # print self.url_get_dept_list
        res = requests.get(self.url_get_dept_list, params=self.__token_params)
        try:
            return res.json()['department']
        except:
            self.__raise_error(res.content)

    def get_dept_detail(self, dept_id):
        params = self.__token_params
        params.update({'id': dept_id})
        res = requests.get(self.url_get_dept_detail, params=params)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def create_dept(self, name, parentid, orderid, createdeptgroup=False):
        payload = self.__token_params
        payload.update({
            'name': name,
            'parentid': parentid,
            'orderid': orderid,
            'createDeptGroup': createdeptgroup,
        })
        res = requests.post(self.url_create_dept, data=payload)
        try:
            return res.json()['id']
        except:
            self.__raise_error(res)

    def delete_dept(self, dept_id):
        params = self.__token_params
        params.update({'id': dept_id})
        res = requests.get(self.url_delete_dept, params=params)
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)

    def get_userid_by_unionid(self, unionid):
        params = self.__token_params
        params.update({'unionid': unionid})
        res = requests.get(self.url_get_user_id_by_unionid, params=params)
        try:
            return res.json()['userid']
        except:
            self.__raise_error(res)

    def get_user_detail(self, userid):
        params = self.__token_params
        params.update({'userid': userid})
        res = requests.get(self.url_get_user_detail, params=params)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def send_message(self,  agentid, messages, userid='', toparty=''):
        payload = {
            'touser': userid,
            'toparty': toparty,
            'agentid': agentid,

            "msgtype": "oa",
            "oa": messages
        }
        headers = {'content-type': 'application/json'}
        params = self.__token_params
        res = requests.post(self.url_send, headers=headers, params=params, data=json.dumps(payload))
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def get_user_count(self, only_active=0):
        params = self.__token_params
        params.update({'onlyActive': only_active})
        res = requests.get(self.url_get_user_count, params=params)
        try:
            return res.json()['count']
        except:
            self.__raise_error(res)

def main(send_to, subject, content):
    try:
        global sendstatus
        global senderr
        data = ''
        messages = {}
        body = {}
        config_file_path = get_path()
        CorpID = read_config(config_file_path, 'ding', "CorpID")
        CorpSecret = read_config(config_file_path, 'ding', "CorpSecret")
        agentid = read_config(config_file_path, 'ding', "agentid")
        web = read_config(config_file_path, 'ding', "web")
        toparty = read_config(config_file_path, 'ding', "toparty")
        content = json.loads(content)
        messages["message_url"] = web
        form = []

        body["content"] = subject
        body["rich"] = {"num": content[u'监控取值']}

        if content[u'当前状态'] == 'PROBLEM':
            messages["head"] = {
                "bgcolor": "DBE97659",  #前两位表示透明度
                "text": "服务器故障"
            }
            body["title"] = "服务器故障"
            form.append({'key': '告警等级：', 'value': content[u'告警等级']})
            form.append({'key': '告警时间：', 'value': content[u'告警时间']})
            form.append({'key': '告警地址：', 'value': content[u'告警地址']})
            form.append({'key': '持续时间：', 'value': content[u'持续时间']})
            form.append({'key': '监控项目：', 'value': content[u'监控项目']})
            body['form'] = form
            body["author"] = content[u'告警主机'] + '故障(' + content[u'事件ID']+ ')'
        else:
            messages["head"] = {
                "bgcolor": "DB00AA00",  #前两位表示透明度
                "text": "服务器恢复"
            }
            body["title"] = "服务器恢复"
            form.append({'key': '告警等级：', 'value': content[u'告警等级']})
            form.append({'key': '恢复时间：', 'value': content[u'恢复时间']})
            form.append({'key': '告警地址：', 'value': content[u'告警地址']})
            form.append({'key': '持续时间：', 'value': content[u'持续时间']})
            form.append({'key': '监控项目：', 'value': content[u'监控项目']})
            body['form'] = form
            body["author"] = content[u'告警主机'] + '恢复(' + content[u'事件ID']+ ')'
        messages['body'] = body
        ding = Dingtalk(CorpID, CorpSecret)
        if toparty == '':
            res = ding.get_dept_list()
            # topartname = read_config(config_file_path, 'ding', "topartname")
            for item in res:
                if item['name'] == send_to:
                    toparty = item['id']
                    write_config(config_file_path, 'ding', "toparty", toparty)
        # print ding.get_dept_list()[1]   #65875499钉邮 66029515 自定义 65875504钉盘
        data = ding.send_message(toparty=toparty, agentid=agentid, messages=messages)
        sendstatus = True
    except Exception, e:
        senderr = str(e)
        sendstatus = False

    logwrite(sendstatus, data)

def get_path():
    path = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_path = path + '/config.ini'
    return config_path

def logwrite(sendstatus, content):
    logpath = '/var/log/zabbix/dingding'
    if not sendstatus:
        content = senderr
    t = datetime.datetime.now()
    daytime = t.strftime('%Y-%m-%d')
    daylogfile = logpath+'/'+str(daytime)+'.log'
    logger = Log(daylogfile, level="info", is_console=False, mbs=5, count=5)
    os.system('chown zabbix.zabbix {0}'.format(daylogfile))
    logger.info(content)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_to = sys.argv[1]
        subject = sys.argv[2]
        content = sys.argv[3]
        logwrite(True, content)
        main(send_to, subject, content)

