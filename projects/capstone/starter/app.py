import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from database.models import setup_db, Shipment, Packager, Carrier
from auth.auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    Packagers
    """
    @app.route('/packagers', methods=['GET'])
    @requires_auth('get:packagers')
    def get_packagers(jwt):
        packagers = [p.format() for p in Packager.query.all()]

        if not packagers:
            abort(404)

        return jsonify({
            "success": True,
            "packagers": packagers
        }), 200

    @app.route('/packagers', methods=['POST'])
    @requires_auth('post:packager')
    def new_packager(jwt):
        body = request.get_json()
        first_name = body.get('first_name', None)
        last_name = body.get('last_name', None)
        initials = body.get('initials', None)
        active = body.get('active', True)

        if not(first_name and initials):
            return jsonify({
                'success': False,
                'error': 422,
                'message': 'First Name and Initials Required'
            }), 422

        try:
            packager = Packager(
                first_name=first_name, last_name=last_name, initials=initials, active=active)
            packager.insert()

            return jsonify({
                'success': True,
                'packager': packager.format()
            })

        except:
            abort(500)

    @app.route('/packagers/<int:packager_id>', methods=['PATCH'])
    @requires_auth('patch:packager')
    def edit_packager(jwt, packager_id):
        packager = Packager.query.filter_by(id=packager_id).one_or_none()
        if packager is None:
            abort(404)

        try:
            body = request.get_json()
            packager.first_name = body.get('first_name', packager.first_name)
            packager.last_name = body.get('last_name', packager.last_name)
            packager.initials = body.get('initials', packager.initials)
            packager.active = body.get('active', packager.active)

            packager.update()

            return jsonify({
                'success': True,
                'packager': packager.format()
            })

        except:
            abort(422)

    """
    Carriers
    """
    @app.route('/carriers', methods=['GET'])
    @requires_auth('get:carriers')
    def get_carriers(jwt):
        carriers = [c.format() for c in Carrier.query.all()]

        if not carriers:
            abort(404)

        return jsonify({
            "success": True,
            "carriers": carriers
        }), 200

    @app.route('/carriers', methods=['POST'])
    @requires_auth('post:carrier')
    def new_carrier(jwt):
        body = request.get_json()
        newname = body.get('name', None)

        if not newname:
            abort(422)

        try:
            carrier = Carrier(name=newname)
            carrier.insert()

            return jsonify({
                "success": True,
                "carrier": carrier.format()
            })

        except:
            abort(500)

    @app.route('/carriers/<int:carrier_id>', methods=['PATCH'])
    @requires_auth('patch:carrier')
    def edit_carrier(jwt, carrier_id):
        carrier = Carrier.query.filter_by(id=carrier_id).one_or_none()
        if carrier is None:
            abort(404)
        try:
            body = request.get_json()
            edited_name = body.get('name', None)

            carrier.name = edited_name
            carrier.update()

            return jsonify({
                'success': True,
                'carrier': carrier.format()
            })

        except:
            abort(422)

    """
    Shipments
    """
    @app.route('/shipments', methods=['GET'])
    @requires_auth('get:shipments')
    def get_shipments(jwt):
        shipments = [s.format() for s in Shipment.query.all()]

        if not shipments:
            abort(404)

        return jsonify({
            "success": True,
            "shipments": shipments
        }), 200

    @app.route('/shipments', methods=['POST'])
    @requires_auth('post:shipments')
    def new_shipment(jwt):
        body = request.get_json()
        data = {
            'reference': body.get('reference', None),
            'carrier_id': body.get('carrier_id', None),
            'packages': body.get('packages', None),
            'weight': body.get('weight', None),
            'tracking': body.get('tracking', None),
            'packaged_by': body.get('packaged_by', None),
            'create_date': body.get('create_date', None)
        }

        # Check which mandatory fields have a null values:
        fields = data.copy()
        fields.pop('tracking')
        fields.pop('create_date')
        nulls = [v for v in fields if fields[v] is None]

        if nulls:
            return jsonify({
                'success': False,
                'error': 422,
                'message': f'Field(s) {nulls} cannot be empty'
            }), 422

        try:
            shipment = Shipment(reference=data['reference'], carrier_id=data['carrier_id'], packages=data['packages'],
                                weight=data['weight'], tracking=data['tracking'], packaged_by=data['packaged_by'], create_date=data['create_date'])
            shipment.insert()

            return jsonify({
                'success': True,
                'shipment': shipment.format()
            })
        except:
            abort(400)

    @app.route('/shipments/<int:shipment_id>', methods=['PATCH'])
    @requires_auth('patch:shipments')
    def edit_shipment(jwt, shipment_id):
        shipment = Shipment.query.filter_by(id=shipment_id).one_or_none()
        if shipment is None:
            abort(404)

        try:
            body = request.get_json()
            shipment.reference = body.get('reference', shipment.reference)
            shipment.carrier_id = body.get('carrier_id', shipment.carrier_id)
            shipment.packages = body.get('packages', shipment.packages)
            shipment.weight = body.get('weight', shipment.weight)
            shipment.tracking = body.get('tracking', shipment.tracking)
            shipment.packaged_by = body.get(
                'packaged_by', shipment.packaged_by)

            shipment.update()

            return jsonify({
                'success': True,
                'shipment': shipment.format()
            })

        except:
            abort(422)

    @app.route('/shipments/<int:shipment_id>', methods=['DELETE'])
    @requires_auth('delete:shipments')
    def del_shipment(jwt, shipment_id):
        shipment = Shipment.query.filter_by(id=shipment_id).one_or_none()
        if shipment is None:
            abort(404)

        try:
            shipment.delete()

            return jsonify({
                'success': True,
                'deleted': shipment.format()
            })

        except:
            abort(422)


# ------------------------
# Error Handlers
# ------------------------

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 401,
            'message': 'unauthorized access'
        }), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Server Error. We crashed.'
        }), 500

    # Snippet from: https://knowledge.udacity.com/questions/331002

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), 401

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
