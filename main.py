import requests
import logging

from sys import argv
from sys import exit

from clockin import HealthCheckInHelper
from exceptions import *

def iyuu_post(iyuu_token):
    url = f"http://iyuu.cn/{iyuu_token}.send"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    def post(text, desp=""):
        form = {'text': text, 'desp': desp}
        return requests.post(url, data=form, headers=headers, verify=False)

    return post

def get_account():
    uid = argv[1]
    psw = argv[2]
    iyuu_token = argv[3]
    return uid, psw, iyuu_token

def main():
    uid, psw, iyuu_token = get_account()
    if iyuu_token.startswith('IYUU'):
        iy_info = iyuu_post(iyuu_token)

    try:
        task = HealthCheckInHelper(uid, psw)
        task.login()
        task.get_old_info()
        resp = task.post()
        if str(resp["e"]) == "0":
            logging.info("clock in successful")
            iy_info("平安浙大：今日已提交", "平安浙大：提交成功")
        else:
            if "今天已经填报了" in str(resp["m"]):
                logging.info(resp["m"])
                iy_info("平安浙大：今日已提交", "平安浙大：今天已经填报了")
                exit(0)
            else:
                logging.error(resp["m"])
                iy_info("平安浙大：提交失败", resp["m"])
                exit(1)
    except LoginException as e:
        logging.error(e)
        iy_info("平安浙大：登录失败", e)
        exit(1)
    except GetInfoException as e:
        logging.error(e)
        iy_info("平安浙大：提交失败", e)
        exit(1)
    except Exception as e:
        logging.error(e)
        iy_info("平安浙大：提交失败", e)
        exit(1)


main()