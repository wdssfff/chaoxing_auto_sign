## 功能描述

**登录方式：**

支持手机号码登录和学号登录

**健康日报：**   

支持腾讯云函数，设置定时触发自动打卡

详情： https://github.com/mkdir700/chaoxing_auto_sign/tree/latest/heath

**课程签到：**

支持普通签到，手势签到，二维码签到，位置签到，拍照签到

支持自定义拍照签到照片及地理位置信息

**微信推送：**

配置server酱key后，签到消息可以推送至您的个人微信

**接口部署：**

使用FastApi框架 和 MongoDB数据库，可以将此项目部署到服务器，通过接口实现多用户多任务签到

## 使用教程

[API版本使用教程](https://github.com/mkdir700/chaoxing_auto_sign/tree/latest/api)

[本地版使用教程](https://github.com/mkdir700/chaoxing_auto_sign/tree/latest/local)

[健康日报使用教程](https://github.com/mkdir700/chaoxing_auto_sign/tree/latest/heath)

## 项目目录

```
|   readme.md
|   start.sh
|
+---.github
|   \---workflows
|           heath-report.yml
|
+---api  # 课堂打卡API版
|   |   cloud_sign.py
|   |   config.py
|   |   db_handler.py
|   |   logs.log
|   |   main.py
|   |   readme.md
|   |   requirements.txt
|   |   sign_request.py
|   |
|
+---heath  # 健康日报打卡
|   |   dev.py
|   |   main.py
|   |   readme.md
|   |
+---local  # 课题打卡本地版
|   |   activeid.json
|   |   config.py
|   |   config1.py
|   |   cookies.json
|   |   local_sign.py
|   |   log.py
|   |   logs.log
|   |   main.py
|   |   message.py
|   |   readme.md
|   |   requirements.txt
|   |
|   +---image
|   |       深度截图_选择区域_20200522103426.png
```

- 多人使用：

需要**部署api**，供自己和其他人使用，可以选择`api`下的脚本

部署参考文章：

https://github.com/mkdir700/chaoxing_auto_sign/blob/master/api/readme.md

- 个人使用：

本地运行，可以选择`local`下的脚本

拍照签到说明：

【本地版】可以自定义拍照签到的上传图片

【Api版】暂时不支持自定义图片，默认【拍照签到】是一张黑色图片

本地版，自定义图片方法

将需要上传的图片文件，放到`image`文件夹中即可，可以放多张图片

遇到拍照签到时，会默认随机抽取一张进行上传，如果`image`下没有图片，默认上传我自己拍摄的一张照片 2333~


## 其他签到脚本推荐


| 项目地址                                                | 开发语言   | 备注                                           |
| ------------------------------------------------------- | ---------- | ---------------------------------------------- |
| https://github.com/PrintNow/ChaoxingSign                | PHP        | PHP版超星自动签到，支持多用户，二次开发便捷！|
| https://github.com/Wzb3422/auto-sign-chaoxing           | TypeScript | 超星学习通自动签到，梦中刷网课       |
| https://github.com/Huangyan0804/AutoCheckin             | Python     | 学习通自动签到，支持手势，二维码，位置，拍照等 |
| https://github.com/aihuahua-522/chaoxing-testforAndroid | Java       | 学习通（超星）自动签到               |
| https://github.com/yuban10703/chaoxingsign              | Python     | 超星学习通自动签到                   |


## 鸣谢

[Jetbrains](https://www.jetbrains.com/)