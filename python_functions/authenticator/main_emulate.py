import flask
from main import authenticator

app = flask.Flask('functions')
methods = ['POST']

@app.route('/authenticator', methods=methods)
@app.route('/authenticator/<path>', methods=methods)
def catch_all(path=''):
    flask.request.path = '/' + path
    return authenticator(flask.request)

if __name__ == '__main__':
    app.run()
