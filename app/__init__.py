import config
from flask import Flask, render_template, redirect, url_for
from flask import flash
from flask_login import LoginManager, login_manager, login_user, login_required, logout_user, current_user

app = Flask(__name__)

from app.models import db, Users, Tasks
from app.forms import UserForm, UserLogin, TaskForm

app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_PATH
app.config["SECRET_KEY"] = config.SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Você precisa entrar com uma conta antes disso!"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).filter_by(id=int(user_id)).first()

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

        flash("Usuário criado com sucesso!", "success")
        form.username.data = ""

    return render_template("auth/user_form.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    form = UserLogin()
    if form.validate_on_submit():
        user = db.session.query(Users).filter(Users.username==form.username.data).first()
        login_user(user)
        flash("Login realizado com sucesso!", "success")
        form.username.data = ""
        return redirect(url_for('index'))

    return render_template("auth/login_form.html", form=form)

@app.route("/logout")
@login_required
def logout():
    flash("Você saiu!", "info")
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
        flash("Item adicionado com sucesso!", "info")
        return redirect(url_for('index'))

    return render_template("task_form.html", form=form)

@app.route("/task/complete/<task_id>")
@login_required
def complete_task(task_id):
    current_task = db.session.query(Tasks).filter_by(id=task_id).first()
    if current_task.user_id == current_user.id:
        current_task.status = 'completed'
        db.session.commit()
        flash("Tarefa concluída com sucesso!", "success")
    else:
        flash("Você não tem permissão para acessar essa página", "warning")
    
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

            flash("Tarefa alterada com sucesso!", "info")
            return redirect(url_for('index'))

        return render_template("update_task.html", form=form, current_task=current_task)
    else:
        flash("Você não tem permissão para acessar essa página", "warning")
        return redirect(url_for('index'))

@app.route("/task/delete/<task_id>")
@login_required
def delete_task(task_id):
    current_task = db.session.query(Tasks).filter_by(id=task_id).first()
    if current_task.user_id == current_user.id:
        db.session.delete(current_task)
        db.session.commit()

        flash("Item excluído com sucesso!", "info")
    else:
        flash("Você não tem permissão para acessar essa página", "warning")

    return redirect(url_for('index'))