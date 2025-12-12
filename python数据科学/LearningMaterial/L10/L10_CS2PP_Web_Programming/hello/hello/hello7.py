from flask import Flask, request, url_for, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # Use templates instead of putting HTML in file.
    # (Try to separate layout/markup from logic.)
    return render_template("index.html")

@app.route("/hello", methods=["GET"])
def hello():
    all_names = request.args.get("first_name").split(",")
    # Default template concatenation escapes risky characters.
    return render_template("hello_all.html", all_names=all_names)

if __name__ == "__main__":
    app.run()
    
