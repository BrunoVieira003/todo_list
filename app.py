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
    return db.session.query(Users).filter_by(id=int(user_id)).first()

# Forms
class UserForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Concluir")

    def validate_username(form, field):
        if db.session.query(Users).filter_by(username=form.username.data).first():
            flash("Nome de usuário já em uso! Tente novamente")
            raise ValidationError("Nome de usuário já em uso!")

class UserLogin(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Concluir")

    def validate_username(form, field):
        if db.session.query(Users).filter_by(username=form.username.data).first() is None:
            flash("Usuário não encontrado! Tente novamente")
            raise ValidationError("Usuário não encontrado")
    
    def validate_password(form, field):
        user = db.session.query(Users).filter_by(username=form.username.data).first()
        if user is not None:
            if user.password != form.password.data:
                flash("Senha incorreta! Tente novamente")
                raise ValidationError("Senha incorreta")

class TaskForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    description = StringField("Descrição")
    submit = SubmitField("Concluir")

# Models
class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)

class Tasks(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(30), nullable=True)
    status = db.Column(db.String(30), nullable=False, default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users')

@app.route("/")
def index():
    task_list = []
    if current_user.is_authenticated:
        task_list = db.session.query(Tasks).filter_by(user_id=current_user.id).order_by(Tasks.status=='completed')

    return render_template("index.html", task_list=task_list)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error404.html"), 404

@app.route("/user/new", methods=["GET","POST"])
def new_user():
    form = UserForm()
    if form.validate_on_submit():
        user = Users()
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
        user = db.session.query(Users).filter(Users.username==form.username.data).first()
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

@app.route("/user/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/user/delete")
@login_required
def delete_user():
    for task in db.session.query(Tasks).filter_by(user_id=current_user.id):
        db.session.delete(task)
    db.session.delete(current_user)
    db.session.commit()
    flash("Sua conta foi excluída com sucesso!")
    logout_user()
    return redirect(url_for('index'))

@app.route("/task/new", methods=["GET", "POST"])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Tasks()
        new_task.title = form.title.data
        new_task.description = form.description.data
        new_task.status = 'pending'
        new_task.user_id = current_user.id
        db.session.add(new_task)
        db.session.commit()

        form.title.data = ''
        form.description.data = ''
        flash("Item adicionado com sucesso!")
        return redirect(url_for('index'))

    return render_template("task_form.html", form=form)

@app.route("/task/complete/<task_id>")
@login_required
def complete_task(task_id):
    current_task = db.session.query(Tasks).filter_by(id=task_id).first()
    if current_task.user_id == current_user.id:
        current_task.status = 'completed'
        db.session.commit()
        flash("Tarefa concluída com sucesso!")
    else:
        flash("Você não tem permissão para acessar essa página")
    
    return redirect(url_for('index'))

@app.route("/task/update/<task_id>", methods=["GET", "POST"])
@login_required
def update_task(task_id):
    form = TaskForm()
    current_task = db.session.query(Tasks).filter_by(id=task_id).first()
    if current_task.user_id == current_user.id:
        if form.validate_on_submit():
            current_task.title = form.title.data
            current_task.description = form.description.data
            db.session.commit()

            flash("Tarefa alterada com sucesso!")
            return redirect(url_for('index'))

        return render_template("update_task.html", form=form, current_task=current_task)
    else:
        flash("Você não tem permissão para acessar essa página")
        return redirect(url_for('index'))

@app.route("/task/delete/<task_id>")
@login_required
def delete_task(task_id):
    current_task = db.session.query(Tasks).filter_by(id=task_id).first()
    if current_task.user_id == current_user.id:
        db.session.delete(current_task)
        db.session.commit()

        flash("Item excluído com sucesso!")
    else:
        flash("Você não tem permissão para acessar essa página")

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)