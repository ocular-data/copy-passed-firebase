import flask
from main import access

app = flask.Flask('functions')
methods = ['POST']


@app.route('/access', methods=methods)
@app.route('/access/<path>', methods=methods)
def catch_all(path=''):
    flask.request.path = '/' + path
    return access(flask.request)


if __name__ == '__main__':
    app.run()
