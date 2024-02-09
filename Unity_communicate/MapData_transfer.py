import flask

# send data to unity by flask

app = flask.Flask(__name__)

@app.route('/send_data', methods=['POST'])
def send_data():
    data = flask.request.get_json()
    print(data)
    return 'success'