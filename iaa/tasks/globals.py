from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kotonebot import Loop

from ._fragments import handle_data_download, handle_notification

def data_download(loop: 'Loop'):
    if handle_data_download():
        return
    elif handle_notification():
        return
