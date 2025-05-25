from flask import Flask
from app.extensiones import mysql
from app.routes.public_routes import public_bp
from app.routes.auth_routes import auth_bp
from app.routes.editor_routes import editor_bp
from app.routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'zapachi_puro_ct'

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '050503'
    app.config['MYSQL_DB'] = 'zapachi_db'

    mysql.init_app(app)

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(admin_bp)

    return app
