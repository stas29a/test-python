#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from challenge import db
import json
from datetime import datetime
import logging
from challenge import models, Session, engine, app

# default to dev config because no one should use this in
# production anyway

manager = Manager(app)
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """

    return dict(app=app, db=db)


@manager.command
def createdb():
    """ Creates a database with all of the tables defined in
        your SQLAlchemy models
    """
    models.Base.metadata.create_all(engine)


@manager.command
def cleandb():
    # здесь бы конечно лучше использовать какой то более автоматический способ вместо явного перечисления
    models.Patient.__table__.drop(engine)
    models.Payment.__table__.drop(engine)


@manager.command
def import_patients():
    # только для теста, в проде нужно из аргумента cli получать путь к файлу
    with open('patients.json') as f:
        session = Session()
        patients = json.load(f)
        patient_collection = []

        for patient in patients:
            date = datetime.strptime(patient['dateOfBirth'], '%Y-%m-%d')
            date = date.date()
            patient_collection.append(
                models.Patient(first_name=patient['firstName'], last_name=patient['lastName'],
                               date_of_birth=date, external_id=patient['externalId'], denormalized_amount=0)
            )

        """
                Здесь можно было бы добавить пересчет суммы транзакций если необходимо сохранять эти данные при этом 
                обновлении. Суть в том, чтобы посчитать это в фоне в виде денормализованного поля и при выборке использовать
                готовое значение вместо динамического суммирования при каждом запросе, обычные реляционные базы такие 
                запросы медленно обрабатывают
        """
        session.begin()
        # ниже строки нужны из-за того что sqlite не умеет truncate, с нормальной базой конечно лучше его выполнять
        models.Patient.__table__.drop(engine)
        models.Patient.metadata.create_all(engine)
        session.bulk_save_objects(patient_collection)
        session.commit()


@manager.command
def import_payments():
    # только для теста, в проде нужно из аргумента cli получать путь к файлу
    with open('payments.json') as f:
        session = Session()

        payments = json.load(f)
        payment_collection = []
        patient_id_to_obj = {}

        # здесь нужно выгрузить так называемые partial объекты, чтобы не передавать лишние данные между бд и приложением
        patients = session.query(models.Patient).all()

        for patient in patients:
            patient_id_to_obj[patient.external_id] = patient

        for payment in payments:
            patient = patient_id_to_obj[payment['patientId']]

            payment_collection.append(
                models.Payment(amount=payment['amount'],
                               patient_id=payment['patientId'],
                               external_id=payment['externalId']
                               )
            )

            print patient
            patient.denormalized_amount += payment['amount']

        session.begin()
        # ниже строки нужны из-за того что sqlite не умеет truncate, с нормальной базой конечно лучше его выполнять
        models.Payment.__table__.drop(engine)
        models.Payment.metadata.create_all(engine)
        session.bulk_save_objects(payment_collection)
        session.bulk_save_objects(patient_id_to_obj.values())

        session.commit()


if __name__ == "__main__":
    manager.run()
