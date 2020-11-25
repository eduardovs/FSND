import os
import datetime
import json
from sqlalchemy import Column, create_engine, CheckConstraint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


database_name = "shipping"
database_path = "postgresql://postgres:sqledu123@{}/{}".format(
    'localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # db.create_all()
    migrate = Migrate(app, db)


'''
Shipments: Records the daily shipping activities
from our shipping department

'''


class Shipment(db.Model):
    __tablename__ = 'shipment'

    id = Column(db.Integer, primary_key=True)
    reference = Column(db.Integer)  # Invoice reference
    carrier_id = Column(db.Integer, db.ForeignKey(
        'carrier.id'), nullable=False)
    packages = Column(db.Integer, CheckConstraint(
        'packages>0'), nullable=False)
    weight = Column(db.Float, CheckConstraint('weight>0'),
                    nullable=False)  # weight in pounds
    tracking = Column(db.String)  # Carrier tracking number
    packaged_by = Column(db.Integer, db.ForeignKey(
        'packager.id'), nullable=False)
    create_date = Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'Reference': self.reference,
            'Weight': self.weight,
            'Packages': self.packages,
            'Packaged By': self.packaged_by,
            'Date': self.create_date

        }


'''
Carrier: 

'''


class Carrier(db.Model):
    __tablename__ = 'carrier'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String, nullable=False)
    active = Column(db.Boolean, default=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # def __init__(self, type):
    #     self.type = type

    def format(self):
        return {
            'id': self.id,
            'Carrier': self.name,
            'is_active': self.active
        }


class Packager(db.Model):
    __tablename__ = 'packager'

    id = Column(db.Integer, primary_key=True)
    first_name = Column(db.String, nullable=False)
    last_name = Column(db.String)
    initials = Column(db.String, nullable=False)
    active = Column(db.Boolean, default=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # def __init__(self, type):
    #     self.type = type

    def format(self):
        return {
            'id': self.id,
            'Packager Initials': self.initials,
            'is_active': self.active


        }

# if __name__ == '__main__':
#     setup_db(app)
