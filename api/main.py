import uvicorn
from fastapi import FastAPI

from cloud_sign import *

app = FastAPI()


@app.post('/sign')
@app.get('/sign')
async def sign(*,
               username: str,
               password: str,
               schoolid=None,
               sckey=None,
               enc=None):
    """
    :params username: 用户名
    :params password: 密码
    :params schoolid: 学校id,
    :params sckey: 推送id,
    :params enc: 二维码签到所需字典
    """
    payload = {
        'username': username,
        'password': password,
        'schoolid': schoolid,
        'sckey': sckey,
        'enc': enc,
    }
    result = await interface(payload)
    return result


uvicorn.run(app)