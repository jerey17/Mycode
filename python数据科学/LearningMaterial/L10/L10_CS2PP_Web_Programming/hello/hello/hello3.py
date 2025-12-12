from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    # Rather than returning plain text, return HTML.
    
    return """
                <html>
                    <head>
                        <title>HTML in a giant string literal.</title>
                    </head>
                    <body>
                        <h1>Hello, World!</h1>
                    </body>
                </html>
           """

if __name__ == "__main__":
    app.run()
    
