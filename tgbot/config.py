from dataclasses import dataclass
from configparser import ConfigParser


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
    selected_operator: int
    channel: str
    group: str
    website: str


@dataclass
class Config:
    tg_bot: TgBot
    db_config: DBConfig


def select_operator(user_id: int | str = 'None'):
    config = ConfigParser()
    config.read('bot.ini')
    config.set('tg_bot', 'selected_operator', str(user_id))
    with open('bot.ini', 'w') as file:
        config.write(file)


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
                     selected_operator=selected_operator,
                     super_user=int(config['tg_bot']['super_user'])),
        db_config=DBConfig(**config['db'])
    )
