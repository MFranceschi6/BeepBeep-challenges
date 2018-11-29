from beepbeep.challenges.database import Challenge
from unittest import mock
from datetime import datetime
import beepbeep
import requests

def get_single_run_dict(user_id=1,run_id=1,start_date=1543334551.0):
    return {
            'average_heartrate': None,
            'average_speed': 10.0,
            'description': 'string',
            'distance': 240.0,
            'elapsed_time': 10,
            'id': run_id, #run_id
            'runner_id': user_id, #user
            'start_date': start_date,
            'strava_id': 1,
            'title': 'run_challenged',
            'total_elevation_gain': 10.0
        }

def get_error_dict(status_code = 404):
    return {'message': 'This is the error description',
            'response-code': status_code}


def check_error(response, status_code, expected_message=None):
    """"
    check error dictionaries returned by flask.
    expected_message param is ignored when status_code is 503
    """""
    json_error = response.get_json()

    if(status_code == 503) :
        return \
            response.status_code == status_code and \
            len(json_error.keys())==3 and \
            json_error['code'] == status_code and \
            json_error['description'] == "The server is temporarily unable to service "\
                + "your request due to maintenance downtime or capacity problems.  "\
                + "Please try again later." and \
            json_error['message'] == "503 Service Unavailable: The server is temporarily unable "\
                + "to service your request due to maintenance downtime or capacity problems.  "\
                + "Please try again later."
    else :
        return \
            response.status_code == status_code and \
            len(json_error.keys())==2 and \
            json_error['response-code'] == status_code and \
            (expected_message is None or expected_message == json_error['message'])


def test_create(client, db_instance):
    """"
    Testing POST /users/{runner_id}/challenges
    """""
    assert db_instance.session.query(Challenge).count() == 0

    #posting (works)
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked1:
        mocked1.return_value = True
        with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked2:
            mocked2.return_value = get_single_run_dict(user_id=1, run_id=33)

            time1 = datetime.today()

            response = client.post('/users/1/challenges', json={
                'run_challenged_id': 33
            })
    assert response.status_code == 200
    assert response.get_json() == 1

    time2 = datetime.today()

    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked:
        mocked.return_value = True
        response = client.get('/users/1/challenges')
    assert response.status_code == 200

    challenge_list = response.get_json()
    assert len(challenge_list) == 1

    challenge0 = challenge_list[0]
    assert challenge0['id'] == 1
    assert challenge0['result'] == False
    assert challenge0['run_challenged_id'] == 33
    assert challenge0['run_challenger_id'] == None
    assert challenge0['runner_id'] == 1
    assert challenge0['start_date'] <= time2.timestamp()
    assert time1.timestamp() <= challenge0['start_date']

    assert db_instance.session.query(Challenge).count() == 1

    challenge = db_instance.session.query(Challenge).first()
    assert challenge.id == 1
    assert challenge.result == False
    assert challenge.run_challenged_id == 33
    assert challenge.run_challenger_id == None
    assert challenge.runner_id == 1
    assert challenge.start_date <= time2
    assert time1 <= challenge.start_date

    #posting when user does not exist
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked1:
        mocked1.return_value = False
        with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked2:
            mocked2.return_value = get_error_dict(status_code=404)

            response = client.post('/users/888/challenges', json={
                'run_challenged_id': 1
            })

            print(response.get_json())
    assert check_error(response,400)

    #posting when user exist & run does not exist
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked1:
        mocked1.return_value = True
        with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked2:
            mocked2.return_value = get_error_dict(status_code=404)

            response = client.post('/users/888/challenges', json={
                'run_challenged_id': 1
            })

            print(response.get_json())
    assert check_error(response,400)

    #posting when an exception is raised
    with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked:
        mocked.side_effect = requests.exceptions.HTTPError(mock.Mock(status=404), 'not found')
        response = client.post('/users/888/challenges', json={
            'run_challenged_id': 1
        })
    assert check_error(response,503)

def test_get_challenge_id(client, db_instance):
    """"
    Testing GET /user/{runner_id}/challenges/{challenge_id}
    """""

    user_id = 99
    run_id = 24
    #posting
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked1:
        mocked1.return_value = True
        with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked2:
            mocked2.return_value = get_single_run_dict(user_id=user_id,run_id=run_id)
            response = client.post('/users/' + str(user_id) + '/challenges', json={
                'run_challenged_id': run_id
            })

    #getting (works)
    response = client.get('/users/' + str(user_id) + '/challenges/1')
    json_data = response.get_json()

    assert len(json_data.keys()) == 6
    assert json_data['id'] == 1
    assert json_data['result'] == False
    assert json_data['run_challenged_id'] == run_id
    assert json_data['run_challenger_id'] == None
    assert json_data['runner_id'] == user_id
    assert isinstance(json_data['start_date'], float)

    #getting (unexisting user)
    response = client.get('/users/88/challenges/1')
    assert check_error(response,404)

    #getting (existing user, unexisting challenge)
    response = client.get('/users/1/challenges/88')
    assert check_error(response,404)

def test_put(client, db_instance):
    """"
    Testing PUT /users/{runner_id}/challenges/{challenge_id}
    First a challenge is created, then some put ops are done.
    """""

    user_id = 4
    challenged_id = 77
    challenger_id = 23

    #posting
    with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked2:
        mocked2.return_value = get_single_run_dict(user_id=user_id,run_id=challenged_id)
        with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked1:
            mocked1.return_value = True
            response = client.post('/users/' + str(user_id) + '/challenges', json={
                'run_challenged_id': challenged_id
            })

    #getting
    response = client.get('/users/' + str(user_id) + '/challenges/1')
    json_data = response.get_json()
    assert json_data['result'] == False

    #putting (not working: challenger is in the past)
    with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked:
        mocked.return_value = get_single_run_dict(user_id=user_id,run_id=challenger_id)
        response = client.put('/users/' + str(user_id) + '/challenges/1', json={
            'run_challenger_id': challenger_id
        })
    assert check_error(response,404)

    #putting (not working: no such challenger exist)
    with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked:
        mocked.return_value = get_error_dict(404)
        response = client.put('/users/' + str(user_id) + '/challenges/1', json={
            'run_challenger_id': challenger_id
        })
    assert check_error(response,404)

    #putting (not working: referred challenge does not exist)
    with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked:
        timestamp = datetime.today().timestamp() + 1
        mocked.return_value = get_single_run_dict(user_id=user_id,run_id=challenger_id,start_date=timestamp)
        response = client.put('/users/' + str(user_id) + '/challenges/99', json={
            'run_challenger_id': challenger_id
        })
    assert check_error(response,404)

    #putting (not working: request exception captured when get_signle_run is invoked)
    with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked:
        mocked.side_effect = requests.exceptions.HTTPError(mock.Mock(status=404), 'not found')
        response = client.put('/users/' + str(user_id) + '/challenges/1', json={
            'run_challenger_id': challenger_id
        })
    json_data = response.get_json()
    assert check_error(response,503)

    #putting (works)
    with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked:
        timestamp = datetime.today().timestamp() + 1
        mocked.return_value = get_single_run_dict(user_id=user_id,run_id=challenger_id,start_date=timestamp)
        response = client.put('/users/' + str(user_id) + '/challenges/1', json={
            'run_challenger_id': challenger_id
        })
    json_data = response.get_json()
    assert len(json_data.keys()) == 6
    assert json_data['run_challenger_id'] == challenger_id

def test_delete(client, db_instance):
    """"
    Testing DELETE /users/{runner_id}/challenges
    """""

    user_id = 99
    run_id_1 = 33
    run_id_2 = 56

    another_user_id = 43
    another_run_id = 8

    #deleting empty db
    response = client.delete('/users/' + str(user_id) + '/challenges')
    print(response.data.decode('ascii'))
    assert response.status_code == 200

    #inserting 3 challenges (2 out of 3 belong to the user)
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked1:
        mocked1.return_value = True
        with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked2:
            mocked2.return_value = get_single_run_dict(user_id=user_id, run_id=run_id_1)
            response = client.post('/users/' + str(user_id) + '/challenges', json={
                'run_challenged_id': run_id_1
            })
            mocked2.return_value = get_single_run_dict(user_id=user_id, run_id=run_id_2)
            response = client.post('/users/' + str(user_id) + '/challenges', json={
                'run_challenged_id': run_id_2
            })
            mocked2.return_value = get_single_run_dict(user_id=another_user_id, run_id=another_run_id)
            response = client.post('/users/' + str(another_user_id) + '/challenges', json={
                'run_challenged_id': another_run_id
            })
    assert db_instance.session.query(Challenge).filter(Challenge.runner_id==user_id).count() == 2

    #deleting challenges of another user
    response = client.delete('/users/' + str(another_user_id) + '/challenges')
    print(response.data.decode('ascii'))
    assert db_instance.session.query(Challenge).filter(Challenge.runner_id==user_id).count() == 2

    #deleting the 2 challenges
    response = client.delete('/users/' + str(user_id) + '/challenges')
    print(response.data.decode('ascii'))
    assert db_instance.session.query(Challenge).filter(Challenge.runner_id==user_id).count() == 0

def test_get(client, db_instance):
    """"
    Testing GET /user/{runner_id}/challenges
    """""
    user_id = 55
    another_user_id = 44

    run_id_list = [23, 34, 45]
    another_run_id_list = [12, 32]

    #getting the empty db
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked:
        mocked.return_value = True
        response = client.get('/users/' + str(user_id) + '/challenges')
    json_data = response.get_json()
    assert json_data == []

    #posting 6 challenges for a user
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked1:
        mocked1.return_value = True
        with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked2:
            for run_id in run_id_list :
                mocked2.return_value = get_single_run_dict(user_id=user_id,run_id=run_id)
                response = client.post('/users/' + str(user_id) + '/challenges', json={
                    'run_challenged_id': run_id
                })
            for another_run_id in another_run_id_list :
                mocked2.return_value = get_single_run_dict(user_id=another_user_id,run_id=another_run_id)
                response = client.post('/users/' + str(user_id) + '/challenges', json={
                    'run_challenged_id': another_run_id
                })

    #getting challenges of the user
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked:
        mocked.return_value = True
        response = client.get('/users/' + str(user_id) + '/challenges')
    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) == len(run_id_list)

    #getting challenges when user does not exist
    with mock.patch('beepbeep.challenges.views.swagger.check_user') as mocked:
        mocked.return_value = False
        response = client.get('/users/' + str(user_id) + '/challenges')
    assert check_error(response,404)

def test_utilities(client, db_instance):
    """"
    Testing utility functions
    """""
    with mock.patch('beepbeep.challenges.views.swagger.get_request_retry') as mocked:
        #check user (not valid user)
        mocked.return_value.json.return_value = {'message': 'This is the error description',\
            'response-code': 404}
        assert beepbeep.challenges.views.swagger.check_user(777) == False

        #check user (valid user)
        mocked.return_value.json.return_value = {
            "age": 42,
            "email": "example@example.com",
            "firstname": "Admin",
            "id": 777,
            "lastname": "Admin",
            "max_hr": 180,
            "report_periodicity": "no",
            "rest_hr": 50,
            "vo2max": 63,
            "weight": 60
        }
        assert beepbeep.challenges.views.swagger.check_user(777) == True

        # check get_single_run
        mocked.return_value.json.return_value = {'message': 'This is the error description',\
            'response-code': 404}
        assert isinstance(beepbeep.challenges.views.swagger.get_single_run(777,3), dict)

    #check date_parsing
    time = datetime(year=2011, month=1, day=15, hour=19, minute=45, second=56)
    assert beepbeep.challenges.views.swagger.date_parsing(time) == '2011-01-15T19:45:56Z'

    # #check determine_result when an exception is captured
    # with mock.patch('beepbeep.challenges.views.swagger.get_single_run') as mocked:
    #     mocked.side_effect = requests.exceptions.HTTPError(mock.Mock(status=404), 'not found')
    #     class Foo:
    #         pass
    #     challenge = Foo()
    #     challenge.runner_id = 123456
    #     challenge.run_challenged_id = 123456
    #     with mock.patch()
    #     return_value = beepbeep.challenges.views.swagger.determine_result(challenge,123456)
    #
    # assert return_value==1
