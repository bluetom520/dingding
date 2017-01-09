ZABBIX可以实现短信、邮件、微信等各种报警，这三种基本大家都很熟悉，但是多多少少受到一些限制，最近受人启发，说可以实现钉钉报警，然后网上找了找，有GO语言大神写得，无奈自己只会三P，所以就用PY交易来实现，苍老师说过：Life is short,you need python!

[TOC]

### 1 钉钉配置
钉钉官网：https://oa.dingtalk.com/
我们主要获取四个参数：部门名称，AgentID和CorpID和CorpSecret
#### 1.1 注册安装
注册钉钉企业号，安装手机钉钉略过
##### 1.1.1 部门设置
在通信录管理里面设置部门，如下图，我们这里设置的**运维部**，这个名称要记住，在ZABBIX里面要配置这个名称，然后把你需要发送告警的人员添加到这个部门里面
![](leanote://file/getImage?fileId=58708444d31d9c3103000000)
##### 1.1.2 应用设置
在企业应用里面有各种应用，如图，发送告警信息可以给下面的各种应用，如钉邮、钉盘
![](leanote://file/getImage?fileId=587084ffd31d9c3103000001)
这里我自己定义了一个应用，服务器报警，记住图中的AgentID，用钉邮、钉盘的AgentID也可以
![](leanote://file/getImage?fileId=58708580d31d9c3103000002)
##### 1.1.3 微应用设置
找到微应用设置，企业应用，CorpID和CorpSecret，点击获取
![](leanote://file/getImage?fileId=58708661d31d9c3103000003)
### 2 程序配置
代码托管到github：https://github.com/bluetom520/dingding
```
git clone https://github.com/bluetom520/dingding.git
pip install requests/requests-2.12.4-py2.py3-none-any.whl
cp dingding/* /usr/lib/zabbix/alertscripts/
chown -R zabbix:zabbix /usr/lib/zabbix/alertscripts/dingding.py
chmod +x   /usr/lib/zabbix/alertscripts/dingding.py
chmod a+w /usr/lib/zabbix/alertscripts/config.ini

```
修改config.ini，把上节获得的三个参数填入，toparty不用填，程序第一次运行会自动获取，web是点击报警信息后跳转的页面，大家用自己，不要老给我发。
```
[ding]
corpid = ding31b4af980259953235c2f4657eb6378f
corpsecret = 5tjFK9oKWptDnh473_2hX3Z_DzZoK2uxhQTqzo6tXf7gd5W6zcOdg8yP-FyjnjfJ
agentid = 66029515
toparty =
web = http://192.168.1.199/zabbix/
```
### 3 ZABBIX配置
#### 3.1 报警媒介类型
到管理-》报警媒介类型配置我们的钉钉
![](leanote://file/getImage?fileId=58708903d31d9c3103000004)
#### 3.2 配置用户
到管理-》用户-》报警媒介-》添加，注意填写收件人为我们之前设置的运维部
![](leanote://file/getImage?fileId=58708952d31d9c3103000005)
#### 3.3 动作设置
到配置-》动作-》创建动作（触发器）
 - 动作
![](leanote://file/getImage?fileId=587089ffd31d9c3103000006)
 - 条件
![](leanote://file/getImage?fileId=58708a1dd31d9c3103000007)
```
服务器:{HOST.NAME}: {TRIGGER.NAME}已恢复!

{
"告警主机":"{HOST.NAME}",
"告警地址":"{HOST.IP}",
"告警时间":"{EVENT.DATE} {EVENT.TIME}",
"恢复时间":"{EVENT.RECOVERY.DATE} {EVENT.RECOVERY.TIME}",
"告警等级":"{TRIGGER.SEVERITY}",
"告警信息":"{TRIGGER.NAME}",
"监控项目":"{ITEM.NAME}",
"当前状态":"{TRIGGER.STATUS}",
"持续时间":"{EVENT.AGE}",
"事件ID":"{EVENT.ID}",
"监控取值":"{ITEM.LASTVALUE}"
}

服务器:{HOST.NAME}发生: {TRIGGER.NAME}故障!

{
"告警主机":"{HOST.NAME}",
"告警地址":"{HOST.IP}",
"告警时间":"{EVENT.DATE} {EVENT.TIME}",
"告警等级":"{TRIGGER.SEVERITY}",
"告警信息":"{TRIGGER.NAME}",
"监控项目":"{ITEM.NAME}",
"当前状态":"{TRIGGER.STATUS}",
"持续时间":"{EVENT.AGE}",
"事件ID":"{EVENT.ID}",
"监控取值":"{ITEM.LASTVALUE}"
}
```
 - 操作
![](leanote://file/getImage?fileId=58708a3ad31d9c3103000008)

### 4 效果展现
故障图
![](leanote://file/getImage?fileId=58708d18d31d9c3103000009)
恢复图
![](leanote://file/getImage?fileId=58708d3ad31d9c310300000b)

### 5 docker环境修改
```
tar zxvf  requests-2.12.4.tar.gz
docker cp requests-2.12.4 zabbix:/usr/local/share/zabbix/alertscripts
docker cp dingding zabbix:/usr/local/share/zabbix/alertscripts
docker exec -it zabbix /bin/bash
cd /usr/local/share/zabbix/alertscripts/requests-2.12.4
rm -rf requests-2.12.4
python setup.py install
cd ..
mv dingding/* .
vi config.ini
exit
docker restart zabbix

```

## 具体内容参考：https://note.gitcloud.cc/blog/post/bluetom520/%E9%92%89%E9%92%89%E6%8A%A5%E8%AD%A6%E6%A8%A1%E6%9D%BF

