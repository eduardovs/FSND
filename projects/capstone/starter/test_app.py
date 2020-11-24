import os
import unittest
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from database.models import setup_db, Shipment, Packager, Carrier
from app import create_app
from auth.auth import AuthError, requires_auth


class ShippingTestCase(unittest.TestCase):
    """
    This class is meant for testing the Shipping App.
    """

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "shipping_test"
        self.database_path = "postgresql://postgres:sqledu123@{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_shipment = {
            "reference": 97900,
            "carrier_id": 6,
            "packages":2, 
            "weight": 40, 
            "tracking": "QWE232323", 
            "packaged_by":3, 
            "create_date":"2020-11-17"
        }

        self.new_packager = {
            "first_name": "Quality",
            "last_name": "Assurance",
            "initials": "QA",
            "active": True
        }

        self.new_carrier = {
            "name": "Test Transport",
            "active": True
        }

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

# Test GET Requests
# -----------------        
    def test_get_shipments(self):
        res = self.client().get('/shipments')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['shipments'], True)

    def test_get_packagers(self):
        res = self.client().get('/packagers')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['packagers'], True)

    def test_get_carriers(self):
        res = self.client().get('/carriers')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['carriers'], True)

# Test POST requests
# ------------------
    def test_new_shipment(self):
        res = self.client().post('/shipments', json=self.new_shipment)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['shipment'], True)

    def test_new_packager(self):
        res = self.client().post('/packagers', json=self.new_packager)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['packager'], True)        


    def test_new_carrier(self):
        res = self.client().post('/carriers', json=self.new_carrier)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['carrier'], True)

# Test PATCH requests
# -------------------
    def test_edit_packager(self):
        res = self.client().patch('/packagers/1', 
            json={
                "first_name": "Jim"
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['packager'], True)        

    def test_edit_carrier(self):
        res = self.client().patch('/carriers/4', 
            json={"name": "Stephan Courier"})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['carrier'], True)

    def test_edit_shipment(self):
        res = self.client().patch('/shipments/2', 
            json={"packages": 7,
                  "weight": 35,
                  "tracking": "PATCHOK25000400"
                })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['shipment'], True)        

# Tear Down
# ---------
    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()







