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
    channel: str
    group: str
    website: str

@dataclass
class Config:
    tg_bot: TgBot
    db_config: DBConfig

def load_config(path: str):
    config = ConfigParser()
    config.read(path)

    return Config(
        tg_bot=TgBot(token=config['tg_bot']['token'],
                     website=config['tg_bot']['website'],
                     group=config['tg_bot']['group'],
                     channel=config['tg_bot']['channel'],
                     super_user=int(config['tg_bot']['super_user'])),
        db_config=DBConfig(**config['db'])
    )
