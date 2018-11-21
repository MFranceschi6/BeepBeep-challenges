import os, requests
from datetime import datetime, date
from .util import bad_response, generate_dataservice_url
from flakon import SwaggerBlueprint
from flask import request, jsonify, redirect
from beepbeep.challenge_microservice.database import db, Challenge
import json
from json import loads


HERE = os.path.dirname(__file__)
YML = os.path.join(HERE, '..', 'static', 'api.yaml')
api = SwaggerBlueprint('API', __name__, swagger_spec=YML)
URL_DATASERVICE = generate_dataservice_url()


def check_user(runner_id):
    url = URL_DATASERVICE + '/user/' + str(runner_id)
    r = requests.get(url)
    result = r.json()
    return 'id' in result

def get_single_run(runner_id, run_id):
    url = URL_DATASERVICE + '/user/' + str(runner_id) + '/runs/' + str(run_id)
    r = requests.get(url)
    result = r.json()
    return result

def get_challenge_of_runner_id(runner_id, challenge_id):
    return db.session.query(Challenge).\
                    filter(Challenge.runner_id == runner_id).\
                    filter(Challenge.id == challenge_id).first()

def date_parsing(date):
    return str(date).replace(" ", "T")+'Z'


@api.operation('createChallenge')
def create_challenge():
    challenge = request.get_json()
    run = get_single_run(challenge['runner_id'], challenge['run_challenged_id'])
    if check_user(challenge['runner_id']) and 'id' in run:
        if run['runner_id'] == challenge['runner_id']:
            db_challenge = Challenge()
            db_challenge.runner_id = challenge['runner_id']
            db_challenge.run_challenged_id = challenge['run_challenged_id']
            db_challenge.start_date = datetime.today()
            db.session.add(db_challenge)
            db.session.commit()
            return "added 1 challenge", 204
    return bad_response(400, 'No user with ID ' + str(challenge['runner_id']) + 'and run' + str(run['runner_id']))


@api.operation('getChallenges')
def get_challenges(runner_id):
    url = URL_DATASERVICE + '/user/' + str(runner_id)
    print("SETTING")
    print(generate_dataservice_url())
    r = requests.get(url)
    result = r.json()
    if 'id' in result:
        challenges = db.session.query(Challenge).filter(Challenge.runner_id == runner_id)
        return jsonify([challenge.to_json() for challenge in challenges])
    return bad_response(404, 'No user with ID ' + str(runner_id))


@api.operation('getChallengeID')
def get_challenge_id(runner_id, challenge_id):
    challenge = get_challenge_of_runner_id(runner_id, challenge_id)
    if challenge is not None:
        return jsonify(challenge.to_json())
    return bad_response(404, 'No challenge with ID ' + str(challenge_id) + ' for user with ID ' + str(runner_id))

#@api.operation('completeChallenge')
#def complete_challenge(runner_id, challenge_id):
#    challenge = get_challenge_of_runner_id(runner_id, challenge_id)
#    if challenge is not None:
#        if challenge.run_challenger_id is None:
#            url = URL_DATASERVICE + '/user/' + str(runner_id) + '/runs'
#            r = requests.get(url, params= {'start-date': date_parsing(challenge.start_date)})
#            results = r.json()
#            return jsonify([result for result in results])
#        else: return jsonify(challenge.to_json())
#    else: return bad_response(404, 'No challenge with ID ' + str(challenge_id) + ' for user with ID ' + str(runner_id))


@api.operation('completeChallenge')
def complete_challenge(runner_id, challenge_id):
    challenge = get_challenge_of_runner_id(runner_id, challenge_id)
    run_challenger_id = request.get_json()['run_challenger_id']
    if challenge is not None:
        if challenge.run_challenger_id is None:
            run = get_single_run(runner_id, run_challenger_id)
            if run is not None and datetime.fromtimestamp(run['start_date']) > challenge.start_date:
                challenge.run_challenger_id = run_challenger_id
                challenge.result = determine_result(challenge, run)
                db.session.commit()
                return jsonify(challenge.to_json())
            else: return bad_response(404, 'No compatible run with ID ' + str(challenge_id) + ' for user with ID ' + str(runner_id))
        else: return jsonify(challenge.to_json())
    else: return bad_response(404, 'No challenge with ID ' + str(challenge_id) + ' for user with ID ' + str(runner_id))

def determine_result(challenge, current_run):
    challenged_run = get_single_run(challenge.runner_id, challenge.run_challenged_id)
    if challenged_run is not None:
        if challenged_run['distance'] == current_run['distance']:
            return challenged_run['average_speed'] < current_run['average_speed']
        elif challenged_run['distance'] < current_run['distance']:
            return challenged_run['average_speed'] <= current_run['average_speed']
        else: return False
    return False