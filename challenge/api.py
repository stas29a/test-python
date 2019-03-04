from flask import Blueprint, jsonify, request
from challenge import models, Session

api = Blueprint('api', __name__)


def patients_get():
    session = Session()
    patients = session.query(models.Patient).all()
    return jsonify(patients)


def patients_post():
    # TODO: implement
    return jsonify({'status': 'OK'})


def payments_get():
    # TODO: implement
    return jsonify([])


def payments_post():
    # TODO: implement
    return jsonify({'status': 'OK'})


@api.route('/patients', methods=['POST', 'GET'])
def patients():
    method = patients_post if request.method == 'POST' else patients_get
    return method()


@api.route('/payments', methods=['POST', 'GET'])
def payments():
    method = payments_post if request.method == 'POST' else payments_get
    return method()
