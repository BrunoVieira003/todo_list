from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
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

class TodoForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    description = TextAreaField("Descrição")
    submit = SubmitField("Concluir")

# Models
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)

class Todos(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(30), nullable=True)
    status = db.Column(db.String(30), nullable=False, default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

@app.route("/")
def index():
    todo_list = []
    if current_user.is_authenticated:
        todo_list = db.session.query(Todos).filter_by(user_id=current_user.id).order_by(Todos.title)

    return render_template("index.html", todo_list=todo_list)

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

@app.route("/todo/new", methods=["GET", "POST"])
@login_required
def new_todo():
    form = TodoForm()
    if form.validate_on_submit():
        new_todo = Todos()
        new_todo.title = form.title.data
        new_todo.description = form.description.data
        new_todo.status = 'pending'
        new_todo.user_id = current_user.id
        db.session.add(new_todo)
        db.session.commit()

        form.title.data = ''
        form.description.data = ''
        flash("Item adicionado com sucesso!")
        return redirect(url_for('index'))

    return render_template("todo_form.html", form=form)

@app.route("/todo/delete/<todo_id>")
@login_required
def delete_todo(todo_id):
    current_todo = db.session.query(Todos).filter_by(id=todo_id).first()
    db.session.delete(current_todo)
    db.session.commit()

    flash("Item excluído com sucesso!")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)