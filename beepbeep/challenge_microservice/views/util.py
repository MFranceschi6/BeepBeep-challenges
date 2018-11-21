import os
from pathlib import Path
from flask import jsonify
import re


def bad_response(code,message):
    return jsonify({'response-code':code, 'message':message}), code

def generate_dataservice_url():
	_HERE = Path(__file__).parents[1]
	_URL_MICROSERVICES = os.path.join(_HERE, 'url_microservices.txt')
	with open(_URL_MICROSERVICES, 'r') as inF: 
		for line in inF:
			if 'URL_DATASERVICE' in line:
				start_index = line.find('=')+1
				end_index = line.rfind('/')
				url = line[start_index : end_index]
	return url



