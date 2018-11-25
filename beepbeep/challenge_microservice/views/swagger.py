import os, requests, json
from datetime import datetime, date
from .util import bad_response
from flakon import SwaggerBlueprint
from flask import request, jsonify, redirect, abort
from beepbeep.challenge_microservice.database import db, Challenge
from json import loads
from flakon.util import retry_request
from flakon.request_utils import users_endpoint, get_request_retry, runs_endpoint, put_request_retry

HERE = os.path.dirname(__file__)
YML = os.path.join(HERE, '..', 'static', 'api.yaml')
api = SwaggerBlueprint('API', __name__, swagger_spec=YML)

def check_user(runner_id):
    r = get_request_retry(users_endpoint(), runner_id)
    result = r.json()
    return 'id' in result

def get_single_run(runner_id, run_id):
    r = get_request_retry(runs_endpoint(runner_id), run_id)
    result = r.json()
    return result

def get_challenge_of_runner_id(runner_id, challenge_id):
    return db.session.query(Challenge).\
                    filter(Challenge.runner_id == runner_id).\
                    filter(Challenge.id == challenge_id).first()

def date_parsing(date):
    return str(date).replace(" ", "T")+'Z'


@api.operation('createChallenge')
def create_challenge(runner_id):
    challenge = request.get_json()
    runner_id = int(runner_id)
    try:
        run = get_single_run(runner_id, challenge['run_challenged_id'])
        if check_user(runner_id) and 'id' in run:
            if run['runner_id'] == runner_id:
                db_challenge = Challenge()
                db_challenge.runner_id = runner_id
                db_challenge.run_challenged_id = challenge['run_challenged_id']
                db_challenge.start_date = datetime.today()
                db.session.add(db_challenge)
                db.session.commit()
                return '', 204
    except requests.exceptions.RequestException as err:
        print(err)
        return abort(503) # SERVICE UNAVAILABLE
    return bad_response(400, 'No user with ID ' + str(runner_id) + 'and run' + str(challenge['run_challenged_id']))


@api.operation('getChallenges')
def get_challenges(runner_id):
    challenges = db.session.query(Challenge).\
                    filter(Challenge.runner_id == runner_id)
    if challenges.count() > 0:
        return jsonify([challenge.to_json() for challenge in challenges])
    return bad_response(404, 'No challenge for user with ID ' + str(runner_id))



@api.operation('getChallengeID')
def get_challenge_id(runner_id, challenge_id):
    challenge = get_challenge_of_runner_id(runner_id, challenge_id)
    if challenge is not None:
        return jsonify(challenge.to_json())
    return bad_response(404, 'No challenge with ID ' + str(challenge_id) + ' for user with ID ' + str(runner_id))

@api.operation('completeChallenge')
def complete_challenge(runner_id, challenge_id):
    challenge = get_challenge_of_runner_id(runner_id, challenge_id)
    run_challenger_id = request.get_json()['run_challenger_id']
    if challenge is not None:
        if challenge.run_challenger_id is None:
            try:
                run = get_single_run(runner_id, run_challenger_id)
            except requests.exceptions.RequestException as err:
                print(err)
                return abort(503)
            if 'start_date' in run:
                if datetime.fromtimestamp(run['start_date']) > challenge.start_date:
                    challenge.run_challenger_id = run_challenger_id
                    challenge.result = determine_result(challenge, run)
                    db.session.commit()
                    return jsonify(challenge.to_json())
                else: return bad_response(404, 'No compatible run for the challenge ' + str(challenge_id) + ' of the user with ID ' + str(runner_id))
            else: return bad_response(404, 'No run with ID ' + str(run_challenger_id) + ' for user with ID ' + str(runner_id))
        else: return jsonify(challenge.to_json())
    else: return bad_response(404, 'No challenge with ID ' + str(challenge_id) + ' for user with ID ' + str(runner_id))

def determine_result(challenge, current_run):
    try:
        challenged_run = get_single_run(challenge.runner_id, challenge.run_challenged_id)
    except requests.exceptions.RequestException as err:
        print(err)
        return abort(503)
    if challenged_run is not None:
        if challenged_run['distance'] == current_run['distance']:
            return challenged_run['average_speed'] < current_run['average_speed']
        elif challenged_run['distance'] < current_run['distance']:
            return challenged_run['average_speed'] <= current_run['average_speed']
        else: return False
    return False

@api.operation('deleteUserChallenges')
def delete_user_challenges(runner_id):
    challenges = db.session.query(Challenge).filter(Challenge.runner_id == runner_id)
    for challenge in challenges:
        db.session.delete(challenge)
        db.session.commit()
    return '', 200
