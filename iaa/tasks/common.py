from kotonebot import logging
from kotonebot.backend.core import HintBox
from kotonebot import device, Loop, action, color
from kotonebot.util import Throttler, Countdown

from . import R
from iaa.context import task_reporter, server

logger = logging.getLogger(__name__)

@action('是否位于首页')
def at_home() -> bool:
    return R.Hud.ButtonLive.find() is not None

@action('返回首页', screenshot_mode='manual')
def go_home(threshold_timeout: float = 0):
    rep = task_reporter()
    rep.message('正在返回首页')
    logger.info('Try to go home.')
    th = Throttler(1)
    cd = Countdown(threshold_timeout)
    for _ in Loop():
        if R.Hud.ButtonLive.find() or (server() == 'tw' and R.Hud.ButtonLiveTwEvent.find()):
            logger.debug('Live button found.')
            break
        elif R.Hud.ButtonGoBack.try_click():
            logger.debug('Go back button found and clicked.')
        else:
            cd.reset()

        if th.request():
            device.click(1, 367)

def has_red_dot(box: HintBox) -> bool:
    return color.find('#ff5589', rect=box) is not None

def hanlde_tip_dialog() -> bool:
    """处理提示对话框。
    类似于第一次进入活动时的说明对话框。

    :return: 如果处理了提示对话框，则返回 True；否则返回 False。
    """
    if btn := (
        R.CommonDialog.ButtonTipDialogNext.find()
        or R.CommonDialog.ButtonTipDialogClose.find()
    ):
        btn.click()
        logger.info('Tip dialog found (button %s) and clicked.', str(btn.prefab))
        return True
    return False
    