import requests
import logging
import re
import json
import time
import datetime
import random

from utils import take_out_json
from exceptions import *

logging.basicConfig(level=logging.INFO)


url_login = "https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex"
url_base = "https://healthreport.zju.edu.cn/ncov/wap/default/index"
url_save = "https://healthreport.zju.edu.cn/ncov/wap/default/save"


class ZJULogin:

    def __init__(self, uid, psw, url_login=url_login):
        """
        parameters:
            * uid: student id
            * psw: password
            * url_login: login page url
        """
        self.uid = uid
        self.psw = psw
        self.url_login = url_login
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        }

        self.session = requests.Session()
        self._init_check()

    def _init_check(self):
        """
        check if the login page is accessible
        """
        logging.info("connect to the url page...")
        resp = self.session.get(self.url_login)

        if resp.status_code == 200:
            logging.info("successful 200 OK")
        else:
            raise LoginException("Fail to open Login Page, Check your Internet connection\n")


    def _rsa_encrypt(self, psw, e_str, M_str):
        """
        encrypt the password with RSA algorithm
        """
        password_bytes = bytes(psw, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16)
        M_int = int(M_str, 16)
        result_int = pow(password_int, e_int, M_int)
        return hex(result_int)[2:].rjust(128, '0')

    def close(self):
        """
        close the session
        """
        self.logout()
        self.session.close()

    def login(self):
        """
        login to ZJU platform
        """
        logging.info("login...")
        resp = self.session.get(self.url_login)
        execution = re.search('name="execution" value="(.*?)"', resp.text).group(1)
        # encrypt the password
        resp = self.session.get('https://zjuam.zju.edu.cn/cas/v2/getPubKey', headers=self.headers).json()
        n = resp["modulus"]
        e = resp["exponent"]
        encrypt_psw = self._rsa_encrypt(self.psw, e, n)
        data = {
            "username": self.uid,
            "password": encrypt_psw,
            "execution": execution,
            "_eventId": "submit"
        }
        resp = self.session.post(url=self.url_login, data=data)
        if "统一身份认证" in resp.content.decode():
            raise LoginException("username or password error")
        else:
            logging.info("login successful")
            return self.session

    def logout(self):
        """
        logout from ZJU platform
        """
        url_logout = "https://zjuam.zju.edu.cn/zjuam-main/security/logout"
        expire = self.session.get(url_logout).headers.get('Set-Cookie')
        if "Expires=Thu, 01-Jan-1970 00:00:00 GMT" in expire:
            logging.info("logout successful")
        else:
            logging.error("logout failed")
        

class HealthCheckInHelper(ZJULogin):

    def __init__(self, uid, psw):
        super().__init__(uid, psw)


    def get_old_info(self):
        resp = self.session.get(url_base, headers=self.headers).content.decode()
        try:
            old_info = re.findall(r'oldInfo: ({[^\n]+})', resp)
            if len(old_info) != 0:
                old_info = json.loads(old_info[0])
            else:
                raise GetInfoException("Fail to get old info")

            new_info = json.loads(re.findall(r'def = ({[^\n]+})', resp)[0])
            new_id = new_info["id"]
            name = re.findall(r'realname: "([^\"]+)",', resp)[0]
            number = re.findall(r"number: '([^\']+)',", resp)[0]
        except json.decoder.JSONDecodeError:
            raise GetInfoException("Fail to get old info: json decode error")
        except IndexError:
            raise GetInfoException("Fail to get old info: index error")

        new_info = old_info.copy()

        # random position
        geo_api_info = json.loads(old_info["geo_api_info"])
        Q = geo_api_info["position"]["Q"] + random.random() * 0.00001
        R = geo_api_info["position"]["R"] + random.random() * 0.00001
        lng = geo_api_info["position"]["lng"] + random.random() * 0.00001
        lat = geo_api_info["position"]["lat"] + random.random() * 0.00001
        geo_api_info["position"]["Q"] = Q
        geo_api_info["position"]["R"] = R
        geo_api_info["position"]["lng"] = lng
        geo_api_info["position"]["lat"] = lat
        new_info["geo_api_info"] = geo_api_info
        # other information
        new_info['id'] = new_id
        new_info['name'] = name
        new_info['number'] = number
        new_info["date"] = self.get_date()
        new_info["created"] = round(time.time())
        new_info['jrdqtlqk[]'] = 0
        new_info['jrdqjcqk[]'] = 0
        new_info['sfsqhzjkk'] = 1   # 是否申领杭州健康码
        new_info['sqhzjkkys'] = 1   # 杭州健康码颜色，1:绿色 2:红色 3:黄色
        new_info['sfqrxxss'] = 1    # 是否确认信息属实
        new_info['jcqzrq'] = ""
        new_info['gwszdd'] = ""
        new_info['szgjcs'] = ""

        magics = re.findall(r'"([0-9a-f]{32})":\s*"([^\"]+)"', resp)
        for item in magics:
            new_info[item[0]] = item[1]

        self.info = new_info
        return new_info
        
    def post(self):
        """Post the hitcard info"""
        res = self.session.post(url_save, data=self.info, headers=self.headers)
        return json.loads(res.text)

    def get_date(self):
        """Get current date"""
        today = datetime.date.today()
        return "%4d%02d%02d" % (today.year, today.month, today.day)

