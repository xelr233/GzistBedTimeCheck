# !/usr/bin/python3
# coding=utf-8
"""
Author: Xe
time: 2025/2/25 23:48
cron: 1 22 * * *
new Env('查寝);
"""

from time import sleep

import execjs
import feapder
import feapder.setting
from feapder.utils.tools import log

import OCR
import getenv

DEBUG = False
with open('v1.js', 'r', encoding='utf-8') as f:
    js = f.read()
ctx = execjs.compile(js)
feapder.setting.USE_SESSION = False
feapder.setting.REQUEST_TIMEOUT = 3
feapder.setting.SPIDER_MAX_RETRY_TIMES = 2
feapder.setting.LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
# 增加错误处理机制，防止在设置日志级别时出现异常
try:
    feapder.setting.LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
except Exception as e:
    log.error(f"设置日志级别失败：{e}")
    feapder.setting.LOG_LEVEL = "INFO"  # 默认设置为INFO级别，确保程序继续运行
feapder.setting.RANDOM_HEADERS = True
feapder.setting.SPIDER_THREAD_COUNT = 1
feapder.setting.SPIDER_SLEEP_TIME = 1


class Config:
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://ids.gzist.edu.cn",
        "Pragma": "no-cache",
        "Referer": "https://ids.gzist.edu.cn/lyuapServer/login",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "\"Google Chrome\";v=\"121\", \"Chromium\";v=\"121\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    get_sid_url = "https://ids.gzist.edu.cn/zuul/docrepo/download"
    get_cap_url = "https://ids.gzist.edu.cn/lyuapServer/kaptcha"
    defult_cooike = {
        "locale": "zh_CN"
    }
    login_url = "https://ids.gzist.edu.cn/lyuapServer/v1/tickets"
    get_cookie_url = "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do"
    update_cookie_url = "https://xsfw.gzist.edu.cn/xsfw/sys/swpubapp/MobileCommon/getSelRoleConfig.do"
    get_info = "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/modules/studentCheckController/queryStudentClassInfo.do"
    check_url = "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/modules/studentCheckController/uniFormSignUp.do"

    data = {
        "username": "",
        "password": "",
        "service": "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do",
        "loginType": "",
        "id": "",
        "code": ""
    }
    user_cookie = {
    }
    bedtime_check_data = {
        "data": "{\"APPID\":\"5405362541914944\",\"APPNAME\":\"swmzncqapp\"}"
    }
    post_data = {
        "data": "{}"
    }


class Account:
    MAX_RETRY_TIMES = 3

    def __init__(self, student_id, password):
        self.student_id = student_id
        self.password = password
        self.data = Config.data.copy()
        self.data["username"] = student_id
        self.data["password"] = ctx.call('encrypt', password)
        self.cookie = Config.defult_cooike.copy()
        self.defalut_cookie = Config.defult_cooike.copy()
        self.retry_times = 0
        self.check_success = False

    def __str__(self) -> str:
        return f"student_id:{self.student_id}"

    def __repr__(self) -> str:
        return self.__str__()

    def need_continue(self) -> bool:
        print(self.retry_times)
        if self.retry_times < Account.MAX_RETRY_TIMES:
            self.retry_times += 1
            return True
        return False


class AccountManager:
    def __init__(self):
        self.get_account_list()
        log.info(f"账号数量：{len(self.account_list)}")
        if self.get_account_quantity() > 0:
            self.current_account_index = 0
        else:
            self.current_account_index = -1
        if DEBUG:
            for i in range(len(self.account_list)):
                self.log_account_info(i)

    def get_account_list(self):

        self.account_list = []
        try:
            for account, password in getenv.get_account_list():
                self.account_list.append(Account(account, password))
        except ValueError as e:
            log.error(f"获取账号密码失败：{e}")

    def get_current_account(self) -> Account:
        return self.account_list[self.current_account_index]

    def get_account_quantity(self) -> int:
        return len(self.account_list)

    def next_account(self) -> bool:
        if self.current_account_index == -1:
            return False
        if self.current_account_index < self.get_account_quantity() - 1:
            self.current_account_index += 1
            return True
        self.current_account_index = -1
        return False

    def log_account_info(self, index) -> None:
        account: Account = self.account_list[index]
        log.info(f"当前账号：{index},账号:{account.student_id},密码:{account.password}")


class BedtimeCheck(feapder.AirSpider):
    def __init__(self):
        super().__init__()
        self.account_manager = AccountManager()

    def continues_request(self, account: Account, request: feapder.Request, back=False) -> feapder.Request:
        sleep(10)
        if account.need_continue():
            if back:
                return feapder.Request(Config.get_sid_url,
                                       callback=self.parse,
                                       )
            return request
        else:
            log.error(f"account: {account} 登录失败,重试次数达到上限")
            log.info(f"开始切换账号")
            sleep(10)
            if self.account_manager.next_account():
                return feapder.Request(Config.get_sid_url,
                                       callback=self.parse,
                                       )
            else:
                return None

    def start_requests(self):  # type: ignore
        yield feapder.Request(Config.get_sid_url,
                              callback=self.parse,
                              )

    def parse(self, request: feapder.Request, response: feapder.Response):  # type: ignore
        sid = response.cookies.get_dict().get('sid')
        account: Account = self.account_manager.get_current_account()
        if not sid:
            log.error(f"获取sid失败：{response.text}")
            yield self.continues_request(account, request)
        account.defalut_cookie['sid'] = sid
        log.debug(f"account: {account} , sid = {sid}")
        yield feapder.Request(Config.get_cap_url,
                              callback=self.parse_cap,
                              cookies=account.defalut_cookie
                              )

    def parse_cap(self, request: feapder.Request, response: feapder.Response):  # type: ignore
        data = response.json
        uid = data.get("uid")
        account: Account = self.account_manager.get_current_account()
        if not uid or not uid:
            log.error(f"获取验证码失败")
            yield self.continues_request(account, request,back=True)
        base64_code = data.get("content").replace("data:image/png;base64,", "")
        log.debug(f"account: {account} , uid={uid}")
        code = OCR.ocr(base64_code)
        log.info(f"account: {account} 验证码为：{code}")
        code = code.replace("=", "")
        try:
            code = eval(code)
        except Exception as e:
            log.error(f"account: {account} 验证码转换失败：{e}")
            yield self.continues_request(account, request,back=True)
        account.data['id'] = uid
        account.data['code'] = code
        yield feapder.Request(Config.login_url,
                              method="POST",
                              data=account.data,
                              callback=self.login,
                              headers=Config.headers,
                              cookies=account.defalut_cookie,
                              )

    def login(self, request: feapder.Request, response: feapder.Response):
        ticket = response.json
        account = self.account_manager.get_current_account()
        if "ticket" not in ticket:
            log.error(f"account: {account} 登录失败,{response.text}")
            yield self.continues_request(account, request, back=True)

        log.debug(f"account:{account} response.text = {response.text}")

        params = {
            "ticket": ticket.get("ticket"),
        }
        log.debug(f"account: {account} , params = {params}")
        yield feapder.Request(Config.get_cookie_url,
                              callback=self.parse_cookie,
                              params=params,
                              headers=Config.headers,
                              cookies=account.cookie,
                              )

    def parse_cookie(self, request: feapder.Request, response: feapder.Response):
        cookies = response.cookies.get_dict()
        account = self.account_manager.get_current_account()
        if not cookies:
            log.error(f"account: {account} 获取cookie失败")
            yield self.continues_request(account, request)
        log.debug(f"account: {account} , cookies={cookies}")
        account.cookie.update(cookies)
        yield feapder.Request(Config.update_cookie_url,
                              method='POST',
                              callback=self.update_cookie,
                              headers=Config.headers,
                              cookies=account.cookie,
                              data=Config.bedtime_check_data,
                              )

    def update_cookie(self, request: feapder.Request, response: feapder.Response):
        cookies = response.cookies.get_dict()
        account = self.account_manager.get_current_account()
        if not cookies:
            log.error(f"account: {account} 更新cookie失败")
            yield self.continues_request(account, request)
        log.debug(f"account: {account} , cookie={cookies}")
        account.cookie.update(cookies)
        yield feapder.Request(Config.check_url,
                              method='POST',
                              callback=self.check,
                              headers=Config.headers,
                              cookies=account.cookie,
                              data=Config.post_data
                              )

    def check(self, request: feapder.Request, response: feapder.Response):
        account = self.account_manager.get_current_account()
        try:
            data = response.json
            code = data.get("code")
            if code == '0':
                account.check_success = True
                log.info(f"account: {account} 查寝成功")
            else:
                msg = data.get("msg")
                log.error(f"account: {account} 查寝失败：{msg}")
        except Exception as e:
            log.error(e)
            log.debug(f"account: {account} 查寝失败：{response.text}")

        if self.account_manager.next_account():
            log.info(f"开始切换账号")
            sleep(10)
            yield feapder.Request(Config.get_sid_url,
                                  callback=self.parse,
                                  )
        return


if __name__ == "__main__":
    log.info("程序开始运行")
    BedtimeCheck().start()
