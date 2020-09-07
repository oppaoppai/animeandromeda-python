from main import app

if __name__ == "__main__":
    app.config["TESTING"] = False
    app.run()
