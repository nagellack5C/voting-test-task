import json
from flask import Flask, request, make_response
from flask_httpauth import HTTPBasicAuth
from .db_client import *

app = Flask(__name__)
auth = HTTPBasicAuth()


'''SERVICE FUNCTIONS'''


@auth.verify_password
def verify_credentials(username, password):
    return db_verify_credentials(username, password)


'''VOTING ENDPOINTS'''


@app.route('/create-voting', methods=['POST'])
@auth.login_required
def create_voting():
    try:
        voting_id = db_create_voting(
            request.json['question'],
            request.json['options'],
            auth.username()
        )
        return f"Vote with id {voting_id} created!", 201
    except KeyError:
        return 'You have not provided the necessary form data!', 400


@app.route('/delete-voting/<voting_id>')
@auth.login_required
def delete_voting(voting_id):
    result = db_delete_voting(voting_id, auth.username())
    if result == 'invalid':
        return 'Invalid id!', 400
    if result:
        return f'Voting with id {voting_id} deleted successfully', 200
    else:
        return 'No such voting found', 404


@app.route('/update-voting/<voting_id>', methods=['POST'])
@auth.login_required
def update_voting(voting_id):
    try:
        result = db_update_voting(
            voting_id,
            auth.username(),
            request.json['question'],
            request.json['options']
        )
        if result == 'invalid':
            return 'Invalid id!', 400
        if result:
            return 'Updated successfully'
        else:
            return 'Didn\'t update', 400
    except KeyError:
        response = make_response(
            'You have not provided the necessary form data!', 400)
        return response


'''USER ENDPOINTS'''


@app.route('/create-user', methods=['POST'])
def create_user():
    try:
        msg = db_create_user(
            request.json['username'],
            request.json['password']
        )
        return msg
    except KeyError:
        return 'You have not provided the necessary form data!', 400


@app.route('/vote/<voting_id>', methods=["POST", "GET"])
def vote(voting_id):
    if request.method == "POST" and verify_credentials(
            request.authorization.username, request.authorization.password
    ):
        try:
            return db_vote(
                auth.username(),
                voting_id,
                request.json["option"]
            )
        except KeyError:
            return 'Please provide an option you vote for', 400
    elif request.method == "GET":
        username = None
        if auth.username():
            username = auth.username()
        result = db_view_voting(voting_id, username)
        if result == 'invalid':
            return 'Invalid id!', 400
        if result:
            result['voting']["_id"] = str(result['voting']["_id"])
            return result
        else:
            return 'No such voting found', 404


'''PUBLIC ENDPOINTS'''


@app.route('/list-votings')
def list_votings():
    username = None
    if auth.username():
        username = auth.username()
    results = db_list_votings(username)
    for result in results:
        result['voting']["_id"] = str(result['voting']["_id"])
    return json.dumps(results)
