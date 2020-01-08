from app import mongo
from app import token
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc
import json
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_current_user, jwt_refresh_token_required,
    verify_jwt_in_request
)
from flask import current_app as app


bp = Blueprint('mail_settings', __name__, url_prefix='/smtp')

@bp.route('/settings/<string:origin>', methods=["PUT", "GET"])
# @token.admin_required
def mail_setings(origin):
    if request.method == "GET":
       mail = mongo.db.mail_settings.find({"origin":origin},{"mail_password":0})
       mail = [serialize_doc(doc) for doc in mail]
       return jsonify (mail)
    if request.method == "PUT":
        if not request.json:
            abort(500)
        if origin == "HR":    
            #checking origin of api hit so if it is HR one smtp conf can be created or updated only
            mail_server = request.json.get("mail_server", None)
            mail_port = request.json.get("mail_port", 0)
            mail_use_tls = request.json.get("mail_use_tls", True)
            mail_username = request.json.get("mail_username", None)
            mail_password = request.json.get("mail_password", None)
            
            if not mail_server and mail_password and mail_port and mail_use_tls and mail_username:
                return jsonify({"msg": "Invalid Request"}), 400    
            
            ret = mongo.db.mail_settings.update({}, {
                "$set": {
                    "mail_server": mail_server,
                    "mail_port": mail_port,
                    "origin": origin,
                    "mail_use_tls": mail_use_tls,
                    "mail_username":mail_username,
                    "mail_password":mail_password
                }
            },upsert=True)
            return jsonify({"MSG":"upsert"}),200
        elif origin == "RECRUIT":
            #checking origin of api hit so if it is RECRUIT multiple smtp conf can be created 
            mail_server = request.json.get("mail_server", None)
            mail_port = request.json.get("mail_port", 0)
            mail_use_tls = request.json.get("mail_use_tls", True)
            mail_username = request.json.get("mail_username", None)
            mail_password = request.json.get("mail_password", None)
            active = request.json.get("active",True)
            
            if not mail_server and mail_password and mail_port and mail_use_tls and mail_username:
                return jsonify({"msg": "Invalid Request"}), 400    
            
            ret = mongo.db.mail_settings.update({"mail_server": mail_server,"origin": "RECRUIT"}, {
                "$set": {
                    "mail_server": mail_server,
                    "mail_port": mail_port,
                    "origin": origin,
                    "mail_use_tls": mail_use_tls,
                    "mail_username":mail_username,
                    "mail_password":mail_password,
                    "active": active
                }
            },upsert=True)
            return jsonify({"MSG":"upsert"}),200
