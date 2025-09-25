
from flask import Flask, jsonify,request
from flask_cors import CORS
from dto.machine_data import MachineDataDTO
from repository.autosoftrep import get_all_machine_data_dto, get_machine_data_dto_by_id,get_machines_dto_by_company_id,get_machines,get_machine_data_by_id_and_time_range,get_company_with_login,get_all_machine_data_by_company_id_dto,get_machines_dto_by_company_id,get_machine_config,update_machine_config,get_all_errors_by_company_id,get_error_by_machine_id,get_machine_parts_by_machine_id,get_occurrences_by_machine_id,get_errors_for_part,get_all_occurrences
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

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"}), 200


#@jwt_required()
def get_all_machine_data():
    results = get_all_machine_data_dto()
    return jsonify(results)

@app.route('/test', methods=['GET'])
def test():
    return jsonify("TEST")

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

import json
from flask import jsonify

@app.route('/api/get_conf_by_machine_id/<int:machine_id>', methods=['GET'])
def get_conf_buy_machine_id(machine_id):
    result = get_machine_config(machine_id)

    # Jeśli None lub pusty – zwróć pustą listę
    if not result:
        return jsonify([])

    # Jeśli to słownik, zwróć bez zmian
    if isinstance(result, dict):
        return jsonify(result)

    # Jeśli to lista, obsłuż dalej
    if isinstance(result, list):
        first_item = result[0]

        # Jeśli elementy to stringi (JSON w stringach)
        if isinstance(first_item, str):
            try:
                parsed_result = [json.loads(item) for item in result]
                return jsonify(parsed_result)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON format in list'}), 500

        # Jeśli elementy to słowniki
        elif isinstance(first_item, dict):
            return jsonify(result)

        else:
            return jsonify({'error': f'Unsupported list item type: {type(first_item)}'}), 500

    # Jeśli typ nieobsługiwany
    return jsonify({'error': f'Unsupported data type: {type(result)}'}), 500

@app.route('/api/get_machines', methods=['GET'])
def get_all_machines():
    result = get_machines()
    return jsonify([item.to_dict() for item in result])
@app.route('/api/set_conf')
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
    
    
@app.route('/api/update_conf_by_machine_id/<int:machine_id>', methods=['POST'])
def update_conf_by_machine_id(machine_id):
    data = request.get_json()

    new_config = data.get('new_config')

    if new_config is None:
        return jsonify({'error': 'Missing new_config in request body'}), 400

    try:
        update_machine_config(machine_id, new_config)
        return jsonify({'status': 'success', 'message': f'Machine {machine_id} config updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Unexpected error', 'details': str(e)}), 500
    

@app.route('/api/get_errors_by_company_id/<int:company_id>', methods=['GET'])
def get_errors_by_company_id(company_id):
    result = get_all_errors_by_company_id(company_id)
    return jsonify([e.__dict__ for e in result])

@app.route('/api/get_errors_by_machine_id/<int:machine_id>', methods=['GET'])
def get_errors_by_machine_id(machine_id):
    result = get_error_by_machine_id(machine_id)
    return jsonify([e.__dict__ for e in result])

@app.route('/api/get_machine_parts_by_machine_id/<int:machine_id>', methods=['GET'])
def api_get_machine_parts_by_machine_id(machine_id):
    result = get_machine_parts_by_machine_id(machine_id)
    return jsonify([p.__dict__ for p in result])

@app.route('/api/get_part_errors/<int:part_id>', methods=['GET'])
def api_get_part_errors(part_id):
    result = get_errors_for_part(part_id)
    return jsonify([e.__dict__ for e in result])

@app.route('/api/get_occurrences_by_machine_id/<int:machine_id>', methods=['GET'])
def api_get_occurrences_by_machine_id(machine_id):
    result = get_occurrences_by_machine_id(machine_id)
    return jsonify([o.__dict__ for o in result])

@app.route('/api/get_all_occurrences', methods=['GET'])
def api_get_all_occurrences():
    result = get_all_occurrences()
    return jsonify([o.__dict__ for o in result])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))#5000
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)


       