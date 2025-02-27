import os
import requests


class WxPusher:
    def __init__(self, app_token=None, uid_list=None):
        # 如果没有手动传入，则从环境变量获取
        self.app_token = app_token or os.getenv('WX_PUSHER_APP_TOKEN')
        if not self.app_token:
            raise ValueError("app_token 不能为空，请提供或设置环境变量")
        
        uid_list_env = os.getenv('WX_PUSHER_UID_LIST', '')
        self.uid_list = uid_list.split('\n') if uid_list else uid_list_env.split('\n')
        if not self.uid_list or (len(self.uid_list) == 1 and self.uid_list[0] == ''):
            raise ValueError("uid_list 不能为空，请提供或设置环境变量")

    def send_message(self, title, msg):
        url = "https://wxpusher.zjiecode.com/api/send/message"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "appToken": self.app_token,
            "content": msg,
            "summary": title,
            "uids": self.uid_list
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            return response.json().get('code') == 1000
        except requests.RequestException as e:
            print(f"请求出错: {e}")
        except ValueError as e:
            print(f"响应解析出错: {e}")
        return False
