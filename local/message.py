def server_chan_send(msgs):
    """server酱将消息推送至微信"""
    desp = ''
    for msg in msgs:
        desp = '|  **课程名**  |   {}   |\r\r| :----------: | :---------- |\r\r'.format(
            msg['name'])
        desp += '| **签到时间** |   {}   |\r\r'.format(msg['date'])
        desp += '| **签到状态** |   {}   |\r\r'.format(msg['status'])
    
    params = {
        'text': '您的网课签到消息来啦！',
        'desp': desp
    }
    requests.get(SERVER_CHAN['url'], params=params)