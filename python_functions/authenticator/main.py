from hashlib import md5
from time import time, sleep

import firebase_admin
from firebase_admin import db
from flask import jsonify
from random import randint
from time import time

firebase_admin.initialize_app(options={
    'databaseURL': 'https://copy-passed.firebaseio.com',
})

waitlist = db.reference('waitlist')
ids = db.reference('ids')

timeoutSeconds = 120


def put(ref, data):
    orig = ref.get()
    if not orig:
        return False
    for i, j in data.items():
        orig[i] = j
    ref.update(orig)
    return True


def add_user(request):
    delBlankw = False
    delBlanki = False

    if waitlist.get() and request.json["id"] in waitlist.get():
        return "Conflict", 409

    if not waitlist.get():
        delBlankw = True
        db.reference().update({"waitlist": {"blank--": 0}})

    if not ids.get():
        delBlanki = True
        db.reference().update({"ids": {"blank--": 0}})


    put(waitlist, {request.json["id"]: "x"})
    start = time()
    # print("entering waitlist")
    while waitlist.child(request.json["id"]).get() == "x":
        sleep(.5)
        if (time() - start) >= timeoutSeconds:
            if delBlanki:
                ids.child("blank--").delete()
            if delBlankw:
                waitlist.child("blank--").delete()
            return "Request Timeout", 408

    uuid = waitlist.child(request.json["id"]).get()
    waitlist.child(request.json["id"]).delete()

    if not ids.get():
        delBlanki = True
        db.reference().update({"ids": {"blank--": 0}})

    idu = get_id(uuid)
    while idu in ids.get():
        idu = get_id(uuid)

    put(ids, {idu: {"uid":uuid,"timestamp":time()}})
    # print(ids)
    if delBlanki:
        ids.child("blank--").delete()
    if delBlankw:
        waitlist.child("blank--").delete()
    return jsonify({"id": idu}), 201


def get_id(oid):
    return md5((str(randint(0, 1e12)) + oid).encode()).hexdigest()


def authenticator(request):
    if not request.json or 'id' not in request.json:
        return "Not Acceptable", 406
    if "revoke" in request.json and request.json["revoke"]:
        if ids.get() and ids.child(request.json["id"]).get():
            ids.child(request.json["id"]).delete()
            return "Deleted", 200
        else:
            return "Not Found", 204
    if request.path == '/' or request.path == '':
        if request.method == 'POST':
            return add_user(request)
        else:
            return 'Method not supported', 405
    return 'URL not found', 404
