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

        self.supervisor_header = {
            "Authorization": "Bearer {}".format(os.getenv('SUPERVISORJWT'))}
        self.packager_header = {
            "Authorization": "Bearer {}".format(os.getenv('PACKAGERJWT'))}

        self.new_shipment = {
            "reference": 97900,
            "carrier_id": 6,
            "packages": 2,
            "weight": 40,
            "tracking": "QWE232323",
            "packaged_by": 3,
            "create_date": "2020-11-17"
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
        res = self.client().get('/shipments', headers=self.packager_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['shipments'], True)

    def test_get_packagers(self):
        res = self.client().get('/packagers', headers=self.packager_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['packagers'], True)

    def test_get_carriers(self):
        res = self.client().get('/carriers', headers=self.packager_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['carriers'], True)

# Test POST requests
# ------------------
    def test_new_shipment(self):
        res = self.client().post('/shipments', json=self.new_shipment,
                                 headers=self.packager_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['shipment'], True)

    def test_new_packager(self):
        res = self.client().post('/packagers', json=self.new_packager,
                                 headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['packager'], True)

    def test_new_carrier(self):
        res = self.client().post('/carriers', json=self.new_carrier,
                                 headers=self.supervisor_header)
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
                                  }, headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['packager'], True)

    def test_edit_carrier(self):
        res = self.client().patch('/carriers/4',
                                  json={"name": "Stephan Courier"}, headers=self.supervisor_header)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['carrier'], True)

    def test_edit_shipment(self):
        res = self.client().patch('/shipments/2',
                                  json={"packages": 7,
                                        "weight": 35,
                                        "tracking": "PATCHOK25000400"
                                        }, headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['shipment'], True)


# Test DELETE requests
# -------------------

    def test_delete_shipment(self):
        res = self.client().delete('/shipments/5', headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)


# Test Error Handling in POST requests
# ------------------------------------

    def test_422_packager(self):
        """Error because of missing data"""
        res = self.client().post('/packagers',
                                 json={"last_name": "Bingo"}, headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertNotIn('packager', data)

    def test_422_carrier(self):
        """Error because of missing data"""
        res = self.client().post('/carriers',
                                 json={"name": ""}, headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertNotIn('carrier', data)

    def test_422_shipment(self):
        """Error because of missing required data:
        carrier_id and packages
        """
        res = self.client().post('/shipments',
                                 json={
                                     "reference": 97900,
                                     "weight": 40,
                                     "tracking": "QWE232323",
                                     "packaged_by": 3,
                                     "create_date": "2020-11-17"
                                 }, headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertNotIn('shipment', data)

    def test_400_shipment(self):
        """Sending invalid foreign keys
        """
        res = self.client().post('/shipments',
                                 json={
                                     "reference": 97999,
                                     "carrier_id": 300,
                                     "packages": 2,
                                     "weight": 4,
                                     "tracking": "QWE232323",
                                     "packaged_by": 555,
                                     "create_date": "2020-11-22"
                                 }, headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertNotIn('shipment', data)

# Test Error Handling in PATCH requests
# -------------------------------------
    def test_404_edit_packager(self):
        """Trying to access a non-existent resource"""
        res = self.client().patch('/packagers/2000',
                                  json={
                                      "first_name": "Jim"
                                  }, headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_404_edit_carrier(self):
        res = self.client().patch('/carriers/8000',
                                  json={"name": "Stephan Courier"}, headers=self.supervisor_header)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_404_edit_shipment(self):
        res = self.client().patch('/shipments/990000',
                                  json={"packages": 7,
                                        "weight": 35,
                                        "tracking": "PATCHOK25000400"
                                        }, headers=self.supervisor_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

# Test Authorization Requests
# ---------------------------

    def test_missing_token(self):
        res = self.client().get('/shipments')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertNotIn('shipment', data)

    def test_401_create_packager(self):
        res = self.client().post('/packagers', json=self.new_packager,
                                 headers=self.packager_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertNotIn('shipment', data)

    def test_401_delete_shipment(self):
        res = self.client().delete('/shipments/5', headers=self.packager_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

# Tear Down
# ---------
    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
