from flask import Flask
from flaskapp_boy_or_girl.config import Config

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	
	from flaskapp_boy_or_girl.main.routes import main
	from flaskapp_boy_or_girl.errors.handlers import errors
	app.register_blueprint(main)
	app.register_blueprint(errors)

	return app