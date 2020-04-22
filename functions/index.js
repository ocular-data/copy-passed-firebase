const functions = require('firebase-functions');

const max_history = 9;

exports.pushHistory = functions.database.ref('/users/{Uid}')
    .onWrite((change, context) => {
        if (!change.before.exists()) {
            return null;
        }
        if (!change.after.exists()) {
            return null;
        }
        if (change.before.child("last").val() === change.after.child("last").val()) {
            return null;
        }

        let before = change.before.val();
        let after = change.after.val();

        after.history = {};
        after.history["1"] = before["last"];

        for (let i = 1; i < max_history; i++) {
            if (!(i.toString() in before.history)) break;
            after.history[(i + 1).toString()] = before.history[i.toString()];
        }

        return change.after.ref.set(after);
    });
