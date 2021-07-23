# !/usr/bin/env python
# --coding:utf-8--

import json
from urllib import request, parse
import requests

APP_ID = "***"
APP_SECRET = "***"
APP_VERIFICATION_TOKEN = "***"


class Bot(object):
    def do_POST(self):
        # 解析请求 body
        # req_body = self.rfile.read(int(self.headers['content-length']))
        # obj = json.loads(req_body.decode("utf-8"))
        # print(req_body)
        #
        # # 校验 verification token 是否匹配，token 不匹配说明该回调并非来自开发平台
        # token = obj.get("token", "")
        # if token != APP_VERIFICATION_TOKEN:
        #     print("verification token not match, token =", token)
        #     self.response("")
        #     return
        #
        # # 根据 type 处理不同类型事件
        # type = obj.get("type", "")
        # if "url_verification" == type:  # 验证请求 URL 是否有效
        #     self.handle_request_url_verify(obj)
        # elif "event_callback" == type:  # 事件回调
        #     # 获取事件内容和类型，并进行相应处理，此处只关注给机器人推送的消息事件
        #     event = obj.get("event")
        #     if event.get("type", "") == "message":
        #         self.handle_message(event)
        #         return
        return

    def handle_request_url_verify(self, post_obj):
        # 原样返回 challenge 字段内容
        challenge = post_obj.get("challenge", "")
        rsp = {'challenge': challenge}
        self.response(json.dumps(rsp))
        return

    def handle_message(self, event):
        # 此处只处理 text 类型消息，其他类型消息忽略
        msg_type = event.get("msg_type", "")
        if msg_type != "text":
            print("unknown msg_type =", msg_type)
            self.response("")
            return

        # 调用发消息 API 之前，先要获取 API 调用凭证：tenant_access_token
        access_token = self.get_tenant_access_token()
        if access_token == "":
            self.response("")
            return

        # 机器人 echo 收到的消息
        self.send_message(access_token, event.get("open_id"), event.get("text"))
        self.response("")
        return

    def response(self, body):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body.encode())

    def get_tenant_access_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"

        headers = {
            "Content-Type": "application/json"
        }
        req_body = {
            "app_id": APP_ID,
            "app_secret": APP_SECRET
        }

        try:
            response = requests.post(url=url, json=req_body, headers=headers)
        except Exception as e:
            print(str(e))
            return ""
        rsp_dict = response.json()
        code = rsp_dict.get("code", -1)
        if code != 0:
            print("get tenant_access_token error, code =", code)
            return ""
        return rsp_dict.get("tenant_access_token", "")

    def get_group_id(self):
        url = 'https://open.feishu.cn/open-apis/chat/v4/list'
        tenant_access_token = self.get_tenant_access_token()
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer " + tenant_access_token
        }
        resp = requests.get(url, headers=headers)
        resp_dict = resp.json()
        print(resp.json)
        return resp_dict["data"]['groups'][0]["chat_id"]

    def send_message(self, token, open_id, text):
        url = "https://open.feishu.cn/open-apis/message/v4/send/"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }
        req_body = {
            "open_id": open_id,
            "msg_type": "text",
            "content": {
                "text": text
            }
        }

        data = bytes(json.dumps(req_body), encoding='utf8')
        req = request.Request(url=url, data=data, headers=headers, method='POST')
        try:
            response = request.urlopen(req)
        except Exception as e:
            print(e.read().decode())
            return

        rsp_body = response.read().decode('utf-8')
        rsp_dict = json.loads(rsp_body)
        code = rsp_dict.get("code", -1)
        if code != 0:
            print("send message error, code = ", code, ", msg =", rsp_dict.get("msg", ""))

    def send_message_card(self):
        url = "https://open.feishu.cn/open-apis/message/v4/send/"
        token = self.get_tenant_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }
        req_body = {
            "chat_id": "oc_89b61cfe6735709cd91a407ef079a403",
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "Demo业务 2021-07-23 发布计划"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "plain_text",
                            "content": "请及时填写发布计划，如已完成，点击完成按钮"
                        },
                        "fields": [
                            {
                                "is_short": False,
                                "text": {
                                    "tag": "lark_md",
                                    "content": "<at id=c99d3a88></at>"
                                },
                            },
                            {
                                "is_short": False,
                                "text": {
                                    "tag": "lark_md",
                                    "content": "<a href=https://pingcap.feishu.cn/docs/doccnxVBXMFXJDHVo7pMq53mhjg>发布计划</a>"
                                }
                            }
                        ]
                    }, {
                        "tag": "action",
                        "actions": [{
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "完成"
                            },
                            "type": "default"
                        }]
                    }
                ]
            }
        }
        try:
            response = requests.post(url=url, json=req_body, headers=headers)
        except Exception as err:
            print(str(err))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bot = Bot()
    bot.send_message_card()
