# BeepBeep-dataservice-challenge

à# This microservice provide the following functionalities for the user:

- Create new Challenge, reachable to /users/<runner_id>/challenges and provining a id run
- Check the challenges of a user, reachable to /users/<runner_id>/challenges
- Delete all the challenges of a user, reachable to /user/<runner_id>/challenges
- Check a specific challenge of a user, reachable to /users/<runner_id>/challenges/<challenge_id>
- Complete a challenge, reachable to /users/<runner_id>/challenges/<challenge_id> and providing another id run
    To complete correctly a challenge is needed to provide a run that has been created later than the creation date of the challenge.

To win a challenge the user must run for longer distance and at least at the same speed than the challenged run
or the user can run for the same distance but must have a speed greater than the challenged run

## To run this microservice
``'
- Open a new terminal and run `data-service`

  ```bash
  cd <YOUR_DIRECTORY>/BeepBeep-challenges/
  pip3 install -r requirements.txt
  python3 setup.py develop
  beepbeep-dataservice-challenge
  ```
