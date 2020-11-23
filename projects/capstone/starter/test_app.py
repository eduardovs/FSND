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

        self.new_shippment = {
            'reference': 97900,
            'carrier_id': 6,
            "packages":2, 
            "weight": 40, 
            "tracking": "QWE232323", 
            "packaged_by":4, 
            "create_date":"2020-11-17"
        }

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        
    def test_get_shipments(self):
        res = self.client().get('/shipments')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['shipments'], True)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()







