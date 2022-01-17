import config
from flask import Flask
from flask_login import LoginManager, login_manager, login_user, login_required, logout_user, current_user

app = Flask(__name__)

from app.models import db, Users, Tasks
from app import views

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