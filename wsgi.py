from flaskr.main import app

if __name__ == "__main__":
    app.config["TESTING"] = True
    app.run()
