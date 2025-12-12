# Import the Flask framework.
from flask import Flask

# Instantiate an application.
app = Flask(__name__)

# This decorator tells Flask that the following function generates a page
# for the URL "/".
@app.route('/')
def index():
    # Return the content of the page.
    # In this case, it's plain text.
    return "Hello World!"

# For testing, run the application in a development server.
if __name__ == "__main__":
    app.run()
    
