from flask import Flask, request, url_for, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # Use templates instead of putting HTML in file.
    # (Try to separate layout/markup from logic.)
    return render_template("index.html")

@app.route("/hello", methods=["GET"])
def hello():
    # Default template concatenation escapes risky characters.
    return render_template("hello.html")

if __name__ == "__main__":
    app.run()
    
