from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, ValidationError
from flask import flash
from flask_login import UserMixin, LoginManager, login_manager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config["SECRET_KEY"] = 'secret'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Você precisa entrar com uma conta antes disso!"

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(id=int(user_id)).first()

# Forms
class UserForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Concluir")

    def validate_username(form, field):
        if db.session.query(User).filter_by(username=form.username.data).first():
            flash("Nome de usuário já em uso! Tente novamente")
            raise ValidationError("Nome de usuário já em uso!")

class UserLogin(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Concluir")

    def validate_username(form, field):
        if db.session.query(User).filter_by(username=form.username.data).first() is None:
            flash("Usuário não encontrado! Tente novamente")
            raise ValidationError("Usuário não encontrado")
    
    def validate_password(form, field):
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user is not None:
            if user.password != form.password.data:
                flash("Senha incorreta! Tente novamente")
                raise ValidationError("Senha incorreta")

# Models
class User(db.Model, UserMixin):
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

@app.route("/login", methods=["GET","POST"])
def login():
    form = UserLogin()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username==form.username.data).first()
        login_user(user)
        flash("Login realizado com sucesso!")
        form.username.data = ""
        return redirect(url_for('index'))

    return render_template("login_form.html", form=form)

@app.route("/logout")
@login_required
def logout():
    flash("Você saiu!")
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)