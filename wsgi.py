from main import app

if __name__ == "__main__":
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
    app.config["TESTING"] = False
    app.run()
