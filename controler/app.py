
from flask import Flask, jsonify,request
from flask_cors import CORS
from dto.machine_data import MachineDataDTO
from repository.autosoftrep import get_all_machine_data_dto, get_machine_data_dto_by_id,get_machines_dto_by_company_id,get_machines,get_machine_data_by_id_and_time_range,get_company_with_login,get_all_machine_data_by_company_id_dto,get_machines_dto_by_company_id
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity 
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "tajny_klucz"  
jwt = JWTManager(app)

USERS = {
    "admin": "password123"
}

#@jwt_required()
def get_all_machine_data():
    results = get_all_machine_data_dto()
    return jsonify(results)

@app.route('/api/get_machine_data_by_company_id/<int:company_id>', methods=['GET'])
def get_machine_data_by_company_id(company_id):
    result = get_all_machine_data_by_company_id_dto(company_id)
    return jsonify([item.__dict__ for item in result])


@app.route('/api/get_machine_data_by_id/<int:machine_id>', methods=['GET'])
def get_machine_data_by_id(machine_id):
    result = get_machine_data_dto_by_id(machine_id)
    return jsonify([item.__dict__ for item in result])

@app.route('/api/get_machines_by_company_id/<int:company_id>', methods=['GET'])
def get_all_machines_by_company_id(company_id):
    result = get_machines_dto_by_company_id(company_id)
    return jsonify([item.to_dict() for item in result])

@app.route('/api/get_machines', methods=['GET'])
def get_all_machines():
    result = get_machines()
    return jsonify([item.to_dict() for item in result])

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify(msg="Brak loginu lub hasla"), 400

    token_data = get_company_with_login(username)
    if not token_data:
        return jsonify(msg="Bledny login lub haslo"), 401

    if token_data.password == password:
        access_token = create_access_token(identity={"company_id": token_data.id, "login": token_data.login})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(msg="Bledny login lub haslo"), 401

def get_machine_data_by_id_and_range(machine_id):
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.fromisoformat(end_time_str)
    result = get_machine_data_by_id_and_time_range(machine_id, start_time, end_time)
    return jsonify([item.__dict__ for item in result])
#todo add task to sc
if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)




       