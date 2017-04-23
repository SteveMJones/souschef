from os import path
from sqlalchemy import create_engine

from config import Config

cfg = Config()
DB_FILE = path.join(cfg.data_dir, "database.db")
engine = create_engine('sqlite:///' + DB_FILE, echo=True)