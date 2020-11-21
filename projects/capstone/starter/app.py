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

    """
    Packagers
    """
    @app.route('/packagers', methods=['GET'])
    def get_packagers():
        packagers = [p.format() for p in Packager.query.all()]

        if not packagers:
            abort(404)

        return jsonify({
            "success": True,
            "packagers": packagers
        }), 200

    @app.route('/packagers', methods=['POST'])
    def new_packager():
        return None

    @app.route('/packagers/<int:packager_id>', methods=['PATCH'])
    def edit_packager():
        return None    


    """
    Carriers
    """
    @app.route('/carriers', methods=['GET'])
    def get_carriers():
        carriers = [c.format() for c in Carrier.query.all()]

        if not carriers:
            abort(404)

        return jsonify({
            "success": True,
            "carriers": carriers
        }), 200

    @app.route('/carriers', methods=['POST'])
    def new_carrier():
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
    def edit_carrier():
        return None
    

    """
    Shipments
    """
    @app.route('/shipments', methods=['GET'])
    def get_shipments():
        shipments = [s.format() for s in Shipment.query.all()]

        if not shipments:
            abort(404)

        return jsonify({
            "success": True,
            "shipments": shipments
        }), 200

    @app.route('/shipments', methods=['POST'])
    def new_shipment():
        return None


    @app.route('/shipments/<int:shipment_id>', methods=['PATCH'])
    def edit_shipment():
        return None 

    @app.route('/shipments/<int:shipment_id>', methods=['DELETE'])
    def del_shipment():
        return None


#------------------------
# Error Handling
#------------------------

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
    app.run(host='0.0.0.0', port=8080, debug=True)