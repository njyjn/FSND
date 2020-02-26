import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import (
    db_drop_and_create_all, setup_db, rollback, close, Drink
)
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["GET"])
@cross_origin()
def get_drinks():
    drinks = Drink.query.all()
    response = {
        "success": True,
        "drinks": [d.short() for d in drinks]
    }
    return jsonify(response)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
        drinks is the list of drinks or appropriate status code indicating
        reason for failure
'''
@app.route('/drinks-detail', methods=["GET"])
@cross_origin()
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    response = {
        "success": True,
        "drinks": [d.long() for d in drinks]
    }
    return jsonify(response)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["POST"])
@cross_origin()
@requires_auth(permission='post:drinks')
def post_drinks(jwt):
    payload = request.get_json()
    print(payload.get('recipe'))
    try:
        drink = Drink(
            title=payload.get('title'),
            recipe=payload.get('recipe')
        )
        drink.insert()
        result = {
            "success": True,
            "drinks": [drink.long()]
        }
    except Exception:
        rollback()
        print(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(result)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
                    "success": False,
                    "error": 500,
                    "message": "internal server error"
                    }), 500


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "not found"
                    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error
                    }), error.status_code
