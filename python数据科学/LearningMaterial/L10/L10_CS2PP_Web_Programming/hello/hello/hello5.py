from flask import Flask, request, url_for

app = Flask(__name__)

@app.route("/")
def index():
    # Use url_for() to avoid hard-coding the URL.
    return """
                <html>
                    <head>
                        <title>Greeter</title>
                    </head>
                    <body>
                        <h1>Welcome</h1>
                        <p>Please enter your name.</p>
                        <form action="{}" method="get">
                            <label for="first_name">Name:</label>
                            <input name="first_name" id="first_name">
                            <input type="submit" value="Submit">
                        </form>
                    </body>
                </html>
           """.format(url_for("hello"))

@app.route("/hello", methods=["GET"])
def hello():
    # Potential security hole here. What if someone passes in nasty JavaScript as a name?
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
    
