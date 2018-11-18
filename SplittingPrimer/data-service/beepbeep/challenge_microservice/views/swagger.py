import os, requests
from datetime import datetime, date

from flakon import SwaggerBlueprint
from flask import request, jsonify, redirect
from beepbeep.challenge_microservice.database import db, Challenge
import json
from json import loads


HERE = os.path.dirname(__file__)
YML = os.path.join(HERE, '..', 'static', 'api.yaml')
api = SwaggerBlueprint('API', __name__, swagger_spec=YML)

def check_user(runner_id):
    url = 'http://127.0.0.1:5002/users/' + str(runner_id)
    r = requests.get(url)
    result = r.json()
    return 'id' in result

def get_run_id(runner_id, run_id):
    url = 'http://127.0.0.1:5002/runs/' + str(runner_id) + '/' + str(run_id)
    r = requests.get(url)
    result = r.json()
    return result

def get_challenge_of_runner_id(runner_id, challenge_id):
    return db.session.query(Challenge).\
                    filter(Challenge.runner_id == runner_id).\
                    filter(Challenge.id == challenge_id).first()



@api.operation('createChallenge')
def create_challenge():
    challenge = request.get_json()
    run = get_run_id(challenge['runner_id'], challenge['run_challenged_id'])
    if check_user(challenge['runner_id']) and 'id' in run:
        if run['runner_id'] == runner_id:
            db_challenge = Challenge()
            db_challenge.runner_id = challenge['runner_id']
            db_challenge.run_challenged_id = challenge['run_challenged_id']
            db_challenge.start_date = date.today()
            db.session.add(db_challenge)
            db.session.commit()
            return {'added': 1}
    return redirect('/')


@api.operation('getChallenges')
def get_challenges(runner_id):
    url = 'http://127.0.0.1:5002/users/' + str(runner_id)
    r = requests.get(url)
    result = r.json()
    if 'id' in result:
        challenges = db.session.query(Challenge).filter(Challenge.runner_id == runner_id)
        return jsonify([challenge.to_json() for challenge in challenges])
    return redirect('/')


@api.operation('getChallengeID')
def get_challenge_id(runner_id, challenge_id):
    challenge = db.session.query(Challenge).\
                    filter(Challenge.runner_id == runner_id).\
                    filter(Challenge.id == challenge_id).first()
    if challenge is not None:
        return jsonify(challenge.to_json())
    return redirect('/')

@api.operation('completeChallenge')
def complete_challenge(runner_id, challenge_id):
    challenge = get_challenge_of_runner_id(runner_id, challenge_id)
    if challenge is not None:
        if challenge.run_challenger_id is None:
            url = 'http://127.0.0.1:5002/runs/' + str(runner_id)
            r = requests.get(url)
            results = r.json()
            results_filtered = [result for result in results if datetime.fromtimestamp(result['start_date']) > challenge.start_date]
            return jsonify([result for result in results_filtered])
        else: return jsonify(challenge.to_json())
    else: return redirect('/')


@api.operation('terminateChallenge')
def terminate_challenge(runner_id, challenge_id):
    challenge = get_challenge_of_runner_id(runner_id, challenge_id)
    run_challenger_id = int(request.get_json()['run_challenger_id'])
    if challenge is not None:
        if challenge.run_challenger_id is None:
            run = get_run_id(runner_id, run_challenger_id)
            if run is not None and datetime.fromtimestamp(run['start_date']) > challenge.start_date:
                challenge.run_challenger_id = run_challenger_id
                challenge.result = determine_result(challenge, run)
                db.session.commit()
                return jsonify(challenge.to_json())
            else: redirect('/')
        else: return jsonify(challenge.to_json())
    else: redirect('/')

def determine_result(challenge, current_run):
    challenged_run = get_run_id(challenge.runner_id, challenge.run_challenged_id)
    if challenged_run is not None:
        if challenged_run['distance'] == current_run['distance']:
            return challenged_run['average_speed'] < current_run['average_speed']
        elif challenged_run['distance'] < current_run['distance']:
            return challenged_run['average_speed'] <= current_run['average_speed']
        else: return False
    return False