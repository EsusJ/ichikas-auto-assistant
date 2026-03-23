import base64
import logging

from kotonebot import device, sleep

from .utils import asset_path

logger = logging.getLogger(__name__)
ADB_KEYBOARD_PKG = 'com.android.adbkeyboard'
ADB_KEYBOARD_ACTIVITY = 'com.android.adbkeyboard/.AdbIME'

def check_installed(pkg: str) -> bool:
    """检查是否安装了指定的包。"""
    d = device.of_android()
    ret = d.commands.adb_shell(f'pm list packages | grep {pkg}')
    return ret.strip() != ''

def install_apk(apk_path: str):
    """安装 APK 文件。"""
    d = device.of_android()
    d.commands.adb.install(apk_path)
    # d.commands.adb_shell(f'push {apk_path} /data/local/tmp/')
    # apk_name = os.path.basename(apk_path)
    # ret = d.commands.adb_shell(f'pm install -r /data/local/tmp/{apk_name}')
    # if 'error' in ret.lower():
    #     raise RuntimeError(f"Failed to install APK: {ret}")

class AdbKeyboardInput:
    def __init__(self) -> None:
        self._checked = False

    def _check(self):
        d = device.of_android()
        if not check_installed(ADB_KEYBOARD_PKG):
            install_apk(asset_path('keyboardservice-debug.apk'))
            sleep(1)
        if not check_installed(ADB_KEYBOARD_PKG):
            raise RuntimeError("Failed to install ADB Keyboard.")
    
    def send(self, text: str):
        self._check()
        c = device.of_android().commands
        old_ime = c.adb_shell('settings get secure default_input_method').strip()
        try:
            c.adb_shell(f'ime enable {ADB_KEYBOARD_ACTIVITY}')
            c.adb_shell(f'ime set {ADB_KEYBOARD_ACTIVITY}')
            encoded_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            c.adb_shell(f'am broadcast -a ADB_INPUT_B64 --es msg "{encoded_text}"')
        finally:
            c.adb_shell(f'ime set {old_ime}')

    def enter(self):
        device.of_android().commands.adb_shell('input keyevent 66')

    def select_all(self):
        device.of_android().commands.adb_shell('input keyevent 29 --longpress')

    def backspace(self):
        device.of_android().commands.adb_shell('input keyevent 67')

    def clear(self):
        self.select_all()
        self.backspace()

    def can_input(self) -> bool | None:
        """判断当前是否处于可输入状态（聚焦于输入框）。

        :return: 布尔值表示，是否可输入。若无法判断，返回 None。
        """
        d = device.of_android()
        ret = d.commands.adb_shell('dumpsys input_method | grep mServedInputConnection')
        ret = ret.strip()
        if ret == 'mServedInputConnectionWrapper=null':
            return False
        elif ret.startswith('mServedInputConnectionWrapper='):
            return True
        else:
            logger.warning(f"Unexpected output from dumpsys input_method: {ret}")
            return None