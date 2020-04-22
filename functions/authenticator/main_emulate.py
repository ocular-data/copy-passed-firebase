import flask
from main import authenticator

app = flask.Flask('functions')
methods = ['POST']

@app.route('/auth', methods=methods)
@app.route('/auth/<path>', methods=methods)
def catch_all(path=''):
    flask.request.path = '/' + path
    return authenticator(flask.request)

if __name__ == '__main__':
    app.run()
