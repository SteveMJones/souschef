from os import path
import logging

from engine import engine, DB_FILE
from model import Base


logger = logging.getLogger('database.util')


def reset():
    logger.debug('reset()')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def init():
    logger.debug('init()')
    if not path.exists(DB_FILE):
        logger.info('Creating database and schema (%s)' % DB_FILE)
        Base.metadata.create_all(engine)


def get_or_create(session, model, **kwargs):
    logger.debug('get_or_create()')
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
        
if __name__ == '__main__':
    init()
