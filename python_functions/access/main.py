import firebase_admin
from firebase_admin import db
from flask import jsonify
from time import time

firebase_admin.initialize_app(options={
    'databaseURL': 'https://copy-passed.firebaseio.com',
})

ids = db.reference('ids')
users = db.reference('users')

deleteAfterDays = 7
deleteAfterSeconds = deleteAfterDays * 86400

def put(ref, data):
    orig = ref.get()
    if not orig:
        return False
    for i, j in data.items():
        orig[i] = j
    ref.update(orig)
    return True


def process_data(request):
    if not request.json or any([i not in request.json for i in ['method', "id"]]):
        return "Not Acceptable", 406

    if ids.get() and request.json["id"] in ids.get():
        uid = ids.child(request.json["id"]).child("uid").get()
    else:
        return "Forbidden", 403

    if request.json["method"] == "get":
        result = {"last": None}
        if users.get() and uid in users.get():
            result = users.child(uid).get()
        return jsonify(result), 202

    elif request.json["method"] == "post":
        if "data" not in request.json:
            return "Not Acceptable", 406

        if not users.get():
            put(db.reference(), {"users": {uid: {"last": "0"}}})
        if not users.child(uid).child("last").get():
            put(users, {uid: {"last": "0"}})
        if not isinstance(request.json["data"], dict):
            data = {"last": request.json["data"]}
        else:
            data = request.json["data"]
        put(users.child(uid), data)

        return jsonify({"success": True}), 200

    else:
        return 'Method not supported', 405


def access(request):
    if ids.get():
        for i, j in ids.get().items():
            if j["timestamp"] <= time() - deleteAfterSeconds:
                ids.child(i).delete()

    if request.path == '/' or request.path == '':
        if request.method == 'POST':
            return process_data(request)
        else:
            return 'Method not supported', 405
    return 'URL not found', 404
