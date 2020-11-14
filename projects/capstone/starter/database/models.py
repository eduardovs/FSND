import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

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
    db.create_all()


'''
Shipments: Records the daily shipping activities
from our shipping department

'''


class Shipment(db.Model):
    __tablename__ = 'shipment'

    id = Column(Integer, primary_key=True)
    reference = Column(Integer) # Invoice reference
    carrier_id = Column(db.Integer, db.ForeignKey(
        'carrier.id'), nullable=False)
    packages = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    tracking = Column(String) # Carrier tracking number
    packaged_by = Column(db.Integer, db.ForeignKey(
        'packager.id'), nullable=False)
    create_date = Column(db.Date, nullable=False)



    # def __init__(self, question, answer, category, difficulty):
    #     self.question = question
    #     self.answer = answer
    #     self.category = category
    #     self.difficulty = difficulty

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
    __tablename__ = 'courier'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

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
            'Carrier': self.name
        }

class Packager(db.Model):
    __tablename__ = 'packager'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    initials = Column(String, nullable=False)

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
            'Packager Initials': self.initials

        }

# if __name__ == '__main__':
#     setup_db(app)

