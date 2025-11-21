from flask import Flask
from controllers.api_controller import api_bp
from controllers.web_controller import web_bp

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.register_blueprint(web_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)