import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
def get_drinks():
    """
    Return shorter detail of all drinks
    """
    try:
        drinks = Drink.query.all()
        drinks_short_format = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_short_format
        }), 200
    except Exception:
        abort(422)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    """
    provides longer drink details to barista who have permission
    """
    try:
        drinks = Drink.query.all()
        drinks_long_format = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_long_format
        }), 200
    except Exception:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """
    Post new drink if manager with post permission
    """
    try:
        body = request.get_json(request)
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if title is None or recipe is None:
            abort(400)
        # check if title is already present
        drink = Drink.query.filter(Drink.title == title).one_or_none()
        if drink:
            abort(400)
        # Create new drink
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()
        new_drink_result = Drink.query.filter(Drink.id == new_drink.id).first()
        drink_long_format = new_drink_result.long()
        return jsonify({
            'success': True,
            'drinks': drink_long_format
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(payload, drink_id):
    """
    Edit drink details if having permission
    """
    try:
        body = request.get_json(request)
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if title is None or recipe is None:
            abort(400)
        # check if id is already present
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        # edit drink
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()
        drink_long_format = drink.long()
        return jsonify({
            'success': True,
            'drinks': drink_long_format
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    """
    Delete drink from database if having permission
    """
    try:
        # check if id is already present
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        # delete drink
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except Exception:
        abort(422)


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


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "unprocresource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error['description']
    }), auth_error.status_code
