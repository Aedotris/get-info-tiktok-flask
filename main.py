from flask import Flask, jsonify
from khang import Users

app = Flask(__name__)
getTiktokUser = Users()

@app.route('/info/<username>')
def get_user_info(username):
    if not username:
        return jsonify({"error": "Username is missing."}), 400

    user_info = getTiktokUser.details(username)
    if not user_info:
        return jsonify({"error": f"User '{username}' not found."}), 404

    return jsonify(user_info)

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"error": "Page not found."}), 404

@app.route('/info')
def info():
    return jsonify({"msg": "Please provide a username in the URL path. Example: /info/@username"})

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
