# -*- coding: utf8 -*-
import re
import asyncio
import logging
import traceback

import aiohttp
from lxml import etree
from bs4 import BeautifulSoup

from config import STATUS_CODE_DICT
from db_handler import *
from sign_request import *


class AutoSign(object):
    
    def __init__(self, username, password, schoolid=None, enc=None):
        """初始化就进行登录"""
        self.headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'}
        self.username = username
        self.password = password
        self.schoolid = '' if schoolid is None else schoolid
        self.enc = '' if enc is None else enc
        self.mongo = SignMongoDB(username)
    
    async def set_cookies(self, client: ClientSession):
        """设置cookies"""
        cookie_status = await self.check_cookies(client)
        if not cookie_status:
            # 无效则重新登录，并保存cookies
            login_resp = await self.login(client)
            if login_resp['code'] == 1000:
                self.save_cookies(login_resp)
            else:
                return 1001
        return 1000
    
    def save_cookies(self, login_resp):
        """保存cookies"""
        resp = login_resp['resp']
        new_cookies = resp.cookies
        cookies = {}
        for key, value in new_cookies.items():
            cookies[key] = value.value
        self.mongo.to_save_cookie(cookies)
    
    async def check_cookies(self, client: ClientSession):
        """验证cookies"""
        # 从数据库内取出cookie
        try:
            cookies = self.mongo.to_get_cookie()
        except:
            return False
        
        # 验证cookies
        async with client.request('GET', 'http://mooc1-1.chaoxing.com/api/workTestPendingNew', allow_redirects=False,
                                  cookies=cookies) as resp:
            code = resp.status
            if code != 200:
                print("cookies失效")
                return False
            else:
                # todo 这一句应该提到外面
                client.cookie_jar.update_cookies(cookies)
                print("cookies有效")
                return True
    
    async def login(self, client: ClientSession):
        """
        登录
        """
        params = {
            'name': self.username,
            'pwd': self.password,
            'schoolid': self.schoolid,
            'verify': 0
        }
        async with client.request('GET',
                                  url='https://passport2.chaoxing.com/api/login',
                                  headers=self.headers,
                                  params=params) as resp:
            text = await resp.text()
            if resp.status == 403:
                return {
                    'code': 1002
                }
            data = json.loads(text)
            if data['result']:
                print("登录成功")
                return {
                    'code': 1000,
                    'msg': '登录成功',
                    'resp': resp
                }  # 登录成功
            else:
                return {
                    'code': 1001,
                    'msg': '登录失败'
                }  # 登录信息有误
    
    def check_activeid(self, activeid: str):
        """验证当前活动id是否已存在"""
        activeid_lists = self.mongo.to_get_istext_activeid()
        if activeid in activeid_lists:
            return True
        else:
            return False
    
    async def get_all_classid(self, client) -> list:
        """获取课程主页中所有课程的classid和courseid"""
        res = []
        # 首先去数据库里寻找
        res = self.mongo.to_get_all_classid_and_courseid()
        if not res:
            
            async with client.request('GET',
                                      'http://mooc1-2.chaoxing.com/visit/interaction',
                                      headers=self.headers) as resp:
                assert resp.status == 200
                text = await resp.text()
            soup = BeautifulSoup(text, "lxml")
            courseId_list = soup.find_all('input', attrs={'name': 'courseId'})
            classId_list = soup.find_all('input', attrs={'name': 'classId'})
            classname_list = soup.find_all('h3', class_="clearfix")
            
            # 用户首次使用，可以将所用有的classid保存
            for i, v in enumerate(courseId_list):
                res.append((v['value'], classId_list[i]['value'],
                            classname_list[i].find_next('a').text))
            self.mongo.to_save_all_classid_and_courseid(res)
        return res
    
    async def get_sign_type(self, classid, courseid, activeid, client):
        """获取签到类型"""
        sign_url = 'https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign'
        params = {
            'activeId': activeid,
            'classId': classid,
            'courseId': courseid
        }
        async with client.request("GET", sign_url, headers=self.headers, params=params) as resp:
            text = await resp.text()
        
        h = etree.HTML(text)
        sign_type = h.xpath('//div[@class="location"]/span/text()')
        return sign_type
    
    async def get_activeid(self, classid, courseid, classname, client):
        """访问任务面板获取课程的活动id"""
        re_rule = r'([\d]+),2'
        async with client.request('GET',
                                  'https://mobilelearn.chaoxing.com/widget/pcpick/stu/index?courseId={}&jclassId={}'.format(
                                      courseid, classid), headers=self.headers, verify_ssl=False) as resp:
            text = await resp.text()
        
        res = []
        h = etree.HTML(text)
        activeid_list = h.xpath('//*[@id="startList"]/div/div/@onclick')
        for activeid in activeid_list:
            activeid = re.findall(re_rule, activeid)
            if not activeid:
                continue
            # 获取签到任务的类型
            sign_type = await self.get_sign_type(classid, courseid, activeid[0], client)
            res.append((activeid[0], sign_type[0]))
        
        n = len(res)
        if n != 0:
            d = {'num': n, 'class': {}}
            for i in range(n):
                if self.check_activeid(res[i][0]):
                    continue
                d['class'][i] = {
                    'classid': classid,
                    'courseid': courseid,
                    'activeid': res[i][0],
                    'classname': classname,
                    'sign_type': res[i][1]
                }
            return d
    
    async def sign_in_type_judgment(self, classid, courseid, activeid, sign_type, client: ClientSession):
        """签到类型的逻辑判断"""
        sign = SignRequest(client, classid, courseid, activeid, sign_type)
        if "手势" in sign_type:
            return await sign.hand_sign()
        elif "二维码" in sign_type:
            return await sign.qcode_sign(self.enc)
        elif "位置" in sign_type:
            return await sign.addr_sign()
        elif "拍照" in sign_type:
            return await sign.tphoto_sign()
        else:
            return await sign.general_sign()
    
    async def start_sign_tasks(self, client):
        """开始所有签到任务"""
        tasks = []
        success = []
        error = []
        # 获取所有课程的classid和course_id
        classid_courseId = await self.get_all_classid(client)
        
        # 使用协程获取所有课程activeid和签到类型
        for i in classid_courseId:
            coroutine = self.get_activeid(i[1], i[0], i[2], client)
            tasks.append(coroutine)
        
        result = await asyncio.gather(*tasks)
        print(result)
        for r in result:
            if r:
                for d in r['class'].values():
                    s = await self.sign_in_type_judgment(
                        d['classid'],
                        d['courseid'],
                        d['activeid'],
                        d['sign_type'],
                        client
                    )
                    if '成功' in STATUS_CODE_DICT[s['status']]:
                        # 签到课程， 签到时间， 签到状态
                        sign_msg = {
                            'name': d['classname'],
                            'date': s['date'],
                            'status': STATUS_CODE_DICT[s['status']]
                        }
                        success.append(sign_msg)
                        # 将签到成功activeid保存至数据库
                        self.mongo.to_save_istext_activeid(d['activeid'])
                    else:
                        sign_msg = {
                            'name': d['classname'],
                            'date': s['date'],
                            'status': STATUS_CODE_DICT[s['status']]
                        }
                        error.append(sign_msg)
        final_msg = []
        if success:
            success_msg = {
                'msg': 2001,
                'detail': success
            }
            final_msg.append(success_msg)
        if error:
            error_msg = {
                'msg': 2002,
                'detail': error
            }
            final_msg.append(error_msg)
        if not final_msg:
            final_msg = {
                'msg': 2000,
                'detail': STATUS_CODE_DICT[2000]
            }
        return final_msg


# def server_chan_send(msgs, sckey=None):
#     """server酱将消息推送至微信"""
#     desp = ''
#     for msg in msgs:
#         desp = '|  **课程名**  |   {}   |\r\r| :----------: | :---------- |\r\r'.format(
#             msg['name'])
#         desp += '| **签到时间** |   {}   |\r\r'.format(msg['date'])
#         desp += '| **签到状态** |   {}   |\r\r'.format(msg['status'])
#
#     params = {
#         'text': '您的网课签到消息来啦！',
#         'desp': desp
#     }
#     if sckey:
#         requests.get('https://sc.ftqq.com/{}.send'.format(sckey), params=params)


async def interface(payload):
    try:
        async with aiohttp.ClientSession() as client:
            auto_sign= AutoSign(username=payload['username'],
                                password=payload['password'],
                                schoolid=payload['schoolid'],
                                enc=payload['enc'])
            login_status = await auto_sign.set_cookies(client)
            if login_status != 1000:
                return {
                    'msg': login_status,
                    'detail': '登录失败，' + STATUS_CODE_DICT[login_status]
                }
            
            result = await auto_sign.start_sign_tasks(client)
        
        return result
    
    except Exception as e:
        logging.basicConfig(filename='logs.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.error(traceback.format_exc())
        traceback.print_exc()
        return {'msg': 4000, 'detail': STATUS_CODE_DICT[4000]}
