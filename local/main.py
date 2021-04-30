import time
import asyncio

import click

from config import *
from local_sign import AutoSign
from log import log_error_msg
from apscheduler.schedulers.blocking import BlockingScheduler


@log_error_msg
async def gen_run(username, password, enc=None):
    """运行"""
    auto_sign = AutoSign(username, password, enc=enc)
    result = await auto_sign.start_sign_task()
    # 关闭会话
    await auto_sign.close_session()
    detail = result['detail']
    return detail


async def local_run():
    tasks = []
    print("=" * 50)
    print("[{}]".format(time.strftime('%Y-%m-%d %H:%M:%S')))
    for info in USER_INFOS:
        coro = gen_run(username=info['username'],
                       password=info['password'],
                       enc=info.get('enc', None))
        tasks.append(coro)
    results = await asyncio.gather(*tasks)
    print("签到状态: {}".format(results))


async def qcode_run(enc):
    tasks = []
    for info in USER_INFOS:
        coro = gen_run(username=info['username'],
                       password=info['password'],
                       enc=enc)
        tasks.append(coro)
    results = await asyncio.gather(*tasks)
    print("签到状态: {}".format(results))


def start():
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()

    loop.run_until_complete(local_run())


@click.group()
def cli():
    pass


@click.command()
def sign():
    """
    立即签到一次
    """
    start()


@click.command()
def timing():
    """
    定时签到任务
    """
    scheduler = BlockingScheduler()
    scheduler.add_job(start, 'interval', hours=i_hours, minutes=i_minutes, seconds=i_seconds)
    print('已开启定时执行,每间隔< {}时{}分{}秒 >执行一次签到任务'.format(i_hours, i_minutes, i_seconds))
    scheduler.start()


@click.command()
@click.option('--enc')
def qcode_sign(enc):
    """
    二维码签到
    """
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(qcode_run(enc))


if __name__ == '__main__':
    cli.add_command(sign)
    cli.add_command(timing)
    cli.add_command(qcode_sign)
    cli()
