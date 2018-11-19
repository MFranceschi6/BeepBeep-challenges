from flask import jsonify


def bad_response(code,message):
    return jsonify({'response-code':code, 'message':message}), code