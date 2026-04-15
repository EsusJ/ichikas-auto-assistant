import logging
import os
import sys
from asyncio import CancelledError

from iaa import __VERSION__
from iaa.config import manager
from iaa.config.base import IaaConfig

logger = logging.getLogger(__name__)

SENTRY_DSN = 'http://efb1a54675734ab18ae8e6732d31dac0@bugsink.1ichika.de/2'


def _root_dir() -> str:
    if not os.path.basename(sys.executable).startswith('python'):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _load_config(config_name: str) -> IaaConfig:
    manager.config_path = os.path.join(_root_dir(), 'conf')
    return manager.read(config_name, not_exist='create')


def is_dev() -> bool:
    return os.path.basename(sys.executable).startswith('python')


def is_enabled(config: IaaConfig | None = None, *, config_name: str = 'default') -> bool:
    conf = config or _load_config(config_name)
    return bool(conf.telemetry.sentry)


def setup(config: IaaConfig | None = None, *, config_name: str = 'default') -> None:
    if is_dev():
        logger.info('Development mode detected, telemetry disabled.')
        return

    conf = config or _load_config(config_name)
    if not conf.telemetry.sentry:
        logger.info('Telemetry disabled or pending consent.')
        return

    import sentry_sdk

    sentry_sdk.init(
        SENTRY_DSN,
        send_default_pii=False,
        max_request_body_size='always',
        server_name='iaa',
        release=__VERSION__,
        traces_sample_rate=0,
        send_client_reports=False,
        auto_session_tracking=False,
        ignore_errors=[KeyboardInterrupt, CancelledError],
    )
    logger.info('Telemetry initialized.')


class _DummySentry:
    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, item):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


def use_sentry():
    if is_dev():
        return _DummySentry()
    import sentry_sdk

    return sentry_sdk
