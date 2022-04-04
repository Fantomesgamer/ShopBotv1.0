from dataclasses import dataclass
from configparser import ConfigParser

from tgbot.handlers.select_operator import OperatorTypes


@dataclass
class DBConfig:
    host: str
    port: str
    database: str
    user: str
    password: str


@dataclass
class TgBot:
    token: str
    super_user: int
    channel: str
    group: str
    website: str


@dataclass
class Config:
    tg_bot: TgBot
    db_config: DBConfig


def select_operator(operator_type: OperatorTypes, user_id: int | str = 'None'):
    config = ConfigParser()
    config.read('bot.ini')
    config.set('operators', f'selected_operator_{operator_type}', str(user_id))
    with open('bot.ini', 'w') as file:
        config.write(file)

def get_selected_operator(operator_type: OperatorTypes) -> int | None:
    config = ConfigParser()
    config.read('bot.ini')
    return config['operators'].get(f'selected_operator_{operator_type}')

def load_config(path: str = 'bot.ini'):
    config = ConfigParser()
    config.read(path)
    if config['tg_bot']['selected_operator'] == 'None':
        selected_operator = None
    else:
        selected_operator = int(config['tg_bot']['selected_operator'])
    return Config(
        tg_bot=TgBot(token=config['tg_bot']['token'],
                     website=config['tg_bot']['website'],
                     group=config['tg_bot']['group'],
                     channel=config['tg_bot']['channel'],
                     super_user=int(config['tg_bot']['super_user'])),
        db_config=DBConfig(**config['db'])
    )
