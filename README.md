# BeepBeep-challenges
Here it is defined the Challenge microservice.
Thanks to this microservice is possible to:
-   create
-   visualize
-   complete
the challenges of a specified user.

This microservice is completely independet from data-service.
It exploits an own database and runs on the port 5003.

To use this microservice is needed put in the setup.py "beepbeep-dataservice-challenge = beepbeep.challenge_microservice.challenge:main" between console scripts

example of utilization:
- http://127.0.0.1:5003/challenges/1
  that allows to visualize all the challenges of the user 1
- http://127.0.0.1:5003/challenges/1/1
  that allows to visualize the challenge 1 of the user 1
- http://127.0.0.1:5003/complete_challenge/1/1
  that allows to visualize the runs that are able to complete the challenge 1 of the user 1
  On the same link but with a POST request, providing a run id, it is possible to complete a challenge
- http://127.0.0.1:5003/create_challenge
  That thanks to a POST request, providing the user_id and a run_id, is possibile to create a new challenge.
