## 环境：

python3.7 , mongodb

## screen

### 安装

centos

```
yum install screen
```



debian,ubuntu

```
apt-get install screen
```



### 进入

创建一个窗口，指令如下

```
screen -S fastapi
```

然后就进入了一个全新的窗口



## 克隆项目

在合适的目录下

```
git clone https://github.com/mkdir700/chaoxing_auto_sign.git
```

![2020/04/15/7a5e50415034311.png](http://cdn.z2blog.com/2020/04/15/7a5e50415034311.png)



## 安装模块

在服务器部署api进入api文件夹

![2020/04/15/b23370415033300.png](http://cdn.z2blog.com/2020/04/15/b23370415033300.png)



使用包管理工具`pip`安装所需模块

```
pip install -r requirements.txt
```



## 运行程序

```
uvicorn main:app --host 0.0.0.0 --port 9090
```

访问`ip:9090`即可访问

![2020/04/15/91c570415033540.png](http://cdn.z2blog.com/2020/04/15/91c570415033540.png)



## 切换回主窗口

程序就一样一直挂就行了，但是我们可能还要进行其他操作

按`Ctrl + A + D` 可切换回之前的主窗口



## 关闭程序

关闭程序，我们需要切换到程序运行窗口

```
screen -r fastapi
```

然后按`Ctrl + C`结束

## 接口使用

```
http://101.89.182.58:9090/sign
```

请求代码示例：
```python
import requests

# POST
params = {
    'username': 'xxxxx',
    'password': 'xxxxx',
    'schoolid': '',
    'sckey': '',
    'enc': ''  #  扫码签到必填
}
requests.post('http://101.89.182.58:9090/sign', params=params)

# GET
username = 'xxx'
password = 'xxx'
requests.get('http://101.89.182.58:9090/sign?username={}&password={}'.format(username, password))
```

在线接口调试：

<http://101.89.182.58:9090/docs#/default/sign_sign_get>


| 请求方式 |   参数   |  说明  | 是否必须 |
| :------: | :------: | :----: | :------: |
|          | username |  账号  |    是    |
|     | password |  密码  |    是    |
|   **POST/GET**       | schoolid | 学校ID |    否    |
| | sckey | server酱key | 否 |
| | enc | 扫码签到参数 | 扫码签到必填 |


**如果是学号登录，fid参数必填**

### 如何获取FID
关于学号登录方式，有一个额外参数`schoolid`

http://passport2.chaoxing.com/login

动图演示：

![2020/04/15/cdf5a0415014614.gif](http://cdn.z2blog.com/2020/04/15/cdf5a0415014614.gif)



## 温馨提示：

1. 如果您的服务器是腾讯云或者阿里云，部署后无法签到，原因是学习通的服务器屏蔽了这两家服务商的ip
2. 如果你所在服务商有安全组规则，请将访问端口设置到安全组(如果安装了宝塔，也需要在宝塔放行访问端口)
3. 部署python程序，建议使用虚拟环境，在虚拟环境中，操作上述步骤，详情python虚拟环境请百度