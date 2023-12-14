from flask import Flask
import config
from exts import db
from blueprints.punch import bp as punch_bp
from blueprints.user import bp as user_bp
from flask_migrate import Migrate
from models import User, Punch, EmailCaptchaModel


app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(punch_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3300)
