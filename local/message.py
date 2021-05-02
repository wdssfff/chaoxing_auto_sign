from config import SERVER_CHAN_SEND_KEY

async def server_chan_send(dataset, session):
    """server酱将消息推送"""
    if SERVER_CHAN_SEND_KEY == '':
        return
    
    if dataset:
        msg = ("| 课程名 | 签到时间 | 签到状态 |\n"
               "| :----: | :------: | :------: |\n")
        msg_template = "|  {}  | {}  |    {}    |"
        for data in dataset:
            msg += msg_template.format(data['name'], data['date'], data['status'])
    else:
        msg = "当前暂无签到任务！"
    
    params = {
        'title': '您的网课签到消息来啦！',
        'desp': msg
    }
    
    async with session.request(
        method="GET",
        url="https://sctapi.ftqq.com/{}.send?title=messagetitle".format(SERVER_CHAN_SEND_KEY),
        params=params
    ) as resp:
        text = await resp.text()