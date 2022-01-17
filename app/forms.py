from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, ValidationError

from app.models import db, Users, Tasks


class UserForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Concluir")

    def validate_username(form, field):
        if db.session.query(Users).filter_by(username=form.username.data).first():
            flash("Nome de usuário já em uso! Tente novamente", "warning")
            raise ValidationError("Nome de usuário já em uso!")

class UserLogin(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Concluir")

    def validate_username(form, field):
        if db.session.query(Users).filter_by(username=form.username.data).first() is None:
            flash("Usuário não encontrado! Tente novamente", "warning")
            raise ValidationError("Usuário não encontrado")
    
    def validate_password(form, field):
        user = db.session.query(Users).filter_by(username=form.username.data).first()
        if user is not None:
            if user.password != form.password.data:
                flash("Senha incorreta! Tente novamente", "warning")
                raise ValidationError("Senha incorreta")

class TaskForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    description = StringField("Descrição")
    submit = SubmitField("Concluir")