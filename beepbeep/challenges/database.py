# encoding: utf8
import os
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
 
class Challenge(db.Model):
    __tablename__ = 'challenge'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    run_challenged_id = db.Column(db.Integer)
    run_challenger_id = db.Column(db.Integer)
    runner_id = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    result = db.Column(db.Boolean, default=False)

    def to_json(self):
        res = {}
        for attr in ('id',
                        'run_challenged_id',
                        'run_challenger_id',
                        'runner_id',
                        'start_date',
                        'result'):
            value = getattr(self, attr)
            if isinstance(value, datetime):
                value = value.timestamp()
            res[attr] = value
        return res


def init_database():
    db.session.commit()


