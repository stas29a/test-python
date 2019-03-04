import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

BaseDB = declarative_base()


class Base(BaseDB):
    __abstract__ = True
    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, server_default=func.now())
    updated = sa.Column(sa.DateTime, onupdate=func.now())


class Patient(Base):
    __tablename__ = 'patients'

    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String)
    date_of_birth = sa.Column(sa.Date)
    external_id = sa.Column(sa.String, unique=True)
    denormalized_amount = sa.Column(sa.Float, nullable=False)


class Payment(Base):
    __tablename__ = 'payments'

    amount = sa.Column(sa.Float, nullable=False)
    patient_id = sa.Column(sa.Integer, sa.ForeignKey('patients.id'), nullable=False)
    external_id = sa.Column(sa.String, index=True)
