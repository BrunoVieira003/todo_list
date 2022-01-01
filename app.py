from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, ValidationError
from flask import flash, redirect

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config["SECRET_KEY"] = 'secret'
db = SQLAlchemy(app)

# Forms
class UserForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Concluir")

    def validate_username(form, field):
        if db.session.query(User).filter_by(username=form.username.data).first():
            flash("Nome de usuário já em uso!")
            raise ValidationError("Nome de usuário já em uso!")

# Models
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error404.html"), 404

@app.route("/user/new", methods=["GET","POST"])
def new_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()

        flash("Usuário criado com sucesso!")
        form.username.data = ""

    return render_template("user_form.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)