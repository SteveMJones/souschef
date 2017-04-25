from os import path

from engine import engine, DB_FILE
from model import Base


def reset():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def init():
    if not path.exists(DB_FILE):
        print 'creating database and schema (%s)' % DB_FILE
        Base.metadata.create_all(engine)


def get_or_create(session, model, **kwargs):
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
