# -*- coding: utf-8 -*-
from flask_user import SQLAlchemyAdapter, UserManager, UserMixin

from perks import app, db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)

    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'',
                      unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False,
                                     server_default='')
    active = db.Column('is_active', db.Boolean(), nullable=False,
                       server_default='0')

    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'',
                     unique=True)
    label = db.Column(db.Unicode(255), server_default=u'')


class UserRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(),
                        db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(),
                        db.ForeignKey('roles.id', ondelete='CASCADE'))


db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)
