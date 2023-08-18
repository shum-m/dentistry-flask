from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from werkzeug.middleware.shared_data import SharedDataMiddleware

app = Flask(__name__, static_folder="uploads")
app.config['SQLALCHEMY_DATABASE_URI'] = "СТРОКА ПОДКЛЮЧЕНИЯ"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'app/uploads/'
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'gif', 'png']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secret string'
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
bootstrap = Bootstrap(app)

from app import views, models
