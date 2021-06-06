from flaskr.main import app
from werkzeug.middleware.proxy_fix import ProxyFix

if __name__ == "__main__":
    app.config["TESTING"] = False
    app = ProxyFix(app, x_for=1, x_proto=1)
    app.run()
