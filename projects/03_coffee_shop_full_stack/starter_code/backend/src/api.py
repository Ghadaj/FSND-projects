import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


## ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
    except:

        abort(500)
    return jsonify({'success': True, 'drinks': drinks})


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-details')
def get_drinks_detail(jwt):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
    except:
        abort(500)
    return jsonify({'success': True, 'drinks': drinks})


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(jwt):
    newDrink = Drink(title=request.json.get('title', ''),
                     recipe=json.dumps(request.json.get('recipe', '')))

    try:
        Drink.insert(newDrink)
    except exc.SQLAlchemyError:


        
        # return internal server error if couldn't add record
        abort(500)

    return jsonify({'success': True, 'drinks': [newDrink.long()]})


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, drink_id):
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if drink is None:

        # Drink with ID is not found

        return (jsonify({'success': False, 'error': 404,
                'message': 'Drink #{} not found.'.format(drink_id)}),
                404)

    if request.json.get('title', '') != '':
        drink.title = request.json.get('title', '')

    if request.json.get('recipe', '') != '':
        drink.recipe = json.dumps(request.json.get('recipe', ''))

    return jsonify({'success': True, 'drinks': [drink.long()]})


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if drink is None:

        # Drink with ID is not found

        return (jsonify({'success': False, 'error': 404,
                'message': 'Drink #{} not found.'.format(drink_id)}),
                404)

    try:
        drink.delete()
    except exc.SQLAlchemyError:

        # return internal server error if couldn't delete record

        abort(500)

    return jsonify({'success': True, 'delete': drink_id})


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({'success': False, 'error': 422,
            'message': 'unprocessable'}), 422)


@app.errorhandler(400)
def error_400(e):
    return (jsonify({'success': False, 'error': 400,
            'message': 'Bad Request'}), 400)


@app.errorhandler(404)
def error_404(e):
    return (jsonify({'success': False, 'error': 404,
            'message': 'Resource not found'}), 404)


@app.errorhandler(500)
def error_500(e):
    return (jsonify({'success': False, 'error': 500,
            'message': 'internal server error'}), 500)


@app.errorhandler(AuthError)
def auth_error(error):
    return (jsonify({'success': False, 'error': error.status_code,
            'message': error.error.get('description', 'unknown error'
            )}), error.status_code)
