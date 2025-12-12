from flask import Flask, request
import sys

app = Flask(__name__)

@app.route("/")
def index():
    # Use the first page to request the user's name.
    return """
                <html>
                    <head>
                        <title>Greeter</title>
                    </head>
                    <body>
                        <h1>Welcome</h1>
                        <p>Please enter your name.</p>
                        <form action="http://localhost:5000/hello" method="get">
                            <label for="first_name">Name:</label>
                            <input name="first_name" id="first_name">
                            <input type="submit" value="Submit">
                        </form>
                    </body>
                </html>
           """

@app.route("/hello", methods=["GET"])
def hello():
    # In the second page, get the user's name from the GET arguments,
    # then concatenate it into the HTML.
    return """
                <html>
                    <head>
                        <title>Welcome</title>
                    </head>
                    <body>
                        <h1>Hello, {}.</h1>
                    </body>
                </html>
           """.format(request.args.get("first_name", "Incognito"))

if __name__ == "__main__":
    app.run()
    
