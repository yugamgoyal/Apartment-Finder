from flask import Flask

app = Flask(__name__)

# Temp API
@app.route('/members')
def members():
    return {'members': ["hi", "hi", "hi"]}

if __name__ == '__main__':
    app.run(debug=True)