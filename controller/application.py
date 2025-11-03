from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from datetime import datetime
import os
# Najpierw import
import repository.autosoftrep

# Teraz sprawdź, skąd Python ładuje moduł
print("Ścieżka do modułu autosoftrep:", repository.autosoftrep.__file__)
from repository.autosoftrep import AutoSoftRepository

# Tworzymy obiekt repozytorium
repo = AutoSoftRepository()
print("Typ repo:", type(repo))
print("Metody repo:", dir(repo))



# ------------------ Flask setup ------------------
app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "tajny_klucz"
jwt = JWTManager(app)

# ------------------ USERS (do testu logowania) ------------------
USERS = {
    "admin": "password123"
}

# ------------------ TEST / PING ------------------
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"}), 200

@app.route('/test', methods=['GET'])
def test():
    return jsonify("TEST")

# ------------------ MACHINE DATA ------------------
@app.route('/api/get_machine_data_by_company_id/<int:company_id>', methods=['GET'])
def get_machine_data_by_company_id(company_id):
    result = repo.get_all_machine_data_by_company_id_dto(company_id)
    return jsonify([item.__dict__ for item in result])

@app.route('/api/get_machine_data_by_id/<int:machine_id>', methods=['GET'])
def get_machine_data_by_id(machine_id):
    result = repo.get_machine_data_dto_by_id(machine_id)
    return jsonify([item.__dict__ for item in result])

@app.route('/api/get_machines_by_company_id/<int:company_id>', methods=['GET'])
def get_all_machines_by_company_id(company_id):
    result = repo.get_machines_dto_by_company_id(company_id)
    return jsonify([item.to_dict() for item in result])

# ------------------ MACHINE CONFIG ------------------
@app.route('/api/get_conf_by_machine_id/<int:machine_id>', methods=['GET'])
def get_conf_by_machine_id(machine_id):
    result = repo.get_machine_config(machine_id)

    if not result:
        return jsonify([])

    if isinstance(result, dict):
        return jsonify(result)

    if isinstance(result, list):
        first_item = result[0]
        if isinstance(first_item, str):
            import json
            try:
                parsed_result = [json.loads(item) for item in result]
                return jsonify(parsed_result)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON format in list'}), 500
        elif isinstance(first_item, dict):
            return jsonify(result)
        else:
            return jsonify({'error': f'Unsupported list item type: {type(first_item)}'}), 500

    return jsonify({'error': f'Unsupported data type: {type(result)}'}), 500

@app.route('/api/update_conf_by_machine_id/<int:machine_id>', methods=['POST'])
def update_conf_by_machine_id(machine_id):
    data = request.get_json()
    new_config = data.get('new_config')
    if new_config is None:
        return jsonify({'error': 'Missing new_config in request body'}), 400
    try:
        repo.update_machine_config(machine_id, new_config)
        return jsonify({'status': 'success', 'message': f'Machine {machine_id} config updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Unexpected error', 'details': str(e)}), 500

# ------------------ ERRORS ------------------
@app.route('/api/get_errors_by_company_id/<int:company_id>', methods=['GET'])
def get_errors_by_company_id(company_id):
    result = repo.get_all_errors_by_company_id(company_id)
    return jsonify([e.__dict__ for e in result])

@app.route('/api/get_errors_by_machine_id/<int:machine_id>', methods=['GET'])
def get_errors_by_machine_id(machine_id):
    result = repo.get_error_by_machine_id(machine_id)
    return jsonify([e.__dict__ for e in result])

@app.route('/api/get_machine_parts_by_machine_id/<int:machine_id>', methods=['GET'])
def api_get_machine_parts_by_machine_id(machine_id):
    result = repo.get_machine_parts_by_machine_id(machine_id)
    return jsonify([p.__dict__ for p in result])

@app.route('/api/get_part_errors/<int:part_id>', methods=['GET'])
def api_get_part_errors(part_id):
    result = repo.get_errors_for_part(part_id)
    return jsonify([e.__dict__ for e in result])

@app.route('/api/get_occurrences_by_machine_id/<int:machine_id>', methods=['GET'])
def api_get_occurrences_by_machine_id(machine_id):
    result = repo.get_occurrences_by_machine_id(machine_id)
    return jsonify([o.__dict__ for o in result])

@app.route('/api/get_all_occurrences', methods=['GET'])
def api_get_all_occurrences():
    result = repo.get_all_occurrences()
    return jsonify([o.__dict__ for o in result])

@app.route('/api/get_error_ids', methods=['GET'])
def api_get_error_ids():
    try:
        part_id = int(request.args.get("part_id"))
        date_from = datetime.fromisoformat(request.args.get("date_from"))
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    result = repo.get_error_ids_for_part_in_date_range(part_id, date_from)
    return jsonify(result)

@app.route('/api/get_error_str', methods=['GET'])
def api_get_error_str():
    try:
        part_id = int(request.args.get("part_id"))
        date_from = datetime.fromisoformat(request.args.get("date_from"))
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    result = repo.get_error_code_for_part_in_date_range(part_id, date_from)
    return jsonify(result)

@app.route('/api/get_error_for_parts', methods=['GET'])
def api_get_error():
    try:
        part_id = int(request.args.get("part_id"))
        date_from = datetime.fromisoformat(request.args.get("date_from"))
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    result = repo.get_occurrences_by_part_id_and_date(part_id, date_from)
    return jsonify(result)

# ------------------ STATS ------------------
@app.route('/api/get_prts_counters', methods=['GET'])
def api_get_stats():
    try:
        machine_id = int(request.args.get("machine_id"))
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    result = repo.get_stats_for_machine(machine_id)
    return jsonify(result)

# ------------------ LOGIN ------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify(msg="Brak loginu lub hasla"), 400

    token_data = repo.get_company_with_login(username)
    if not token_data:
        return jsonify(msg="Bledny login lub haslo"), 401

    if token_data.password == password:
        access_token = create_access_token(identity={"company_id": token_data.id, "login": token_data.login})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(msg="Bledny login lub haslo"), 401

# ------------------ RUN ------------------
@app.route('/api/get_last_errors/<int:machine_id>', methods=['GET'])
def api_get_last_errors(machine_id):
    # Pobieramy ostatnie 10 błędów z repozytorium
    errors = repo.get_last_errors(machine_id)

    # Filtrujemy duplikaty po error_code i zostawiamy maks. 4 ostatnie
    unique_errors = []
    seen_codes = set()

    for error in errors:
        if error.error_code not in seen_codes:
            unique_errors.append(error)
            seen_codes.add(error.error_code)
        if len(unique_errors) == 4:
            break

    # Zamiana DTO na dict, żeby Flask mógł jsonify
    return jsonify([e.__dict__ for e in unique_errors]), 200

@app.route('/api/get_error_for_machine', methods=['GET'])
def api_get_error_mahine_and_time():
    try:
        machine_id = int(request.args.get("machine_id"))
        date_from = datetime.fromisoformat(request.args.get("date_from"))
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    result = repo.get_error_code_for_machine_in_date_range(machine_id, date_from)
    return  jsonify([e.__dict__ for e in  result]), 200


##POST
@app.route('/api/update_machine_part_stat', methods=['POST'])
def api_update_machine_part_stat():
    """
    Aktualizuje statystyki części maszyny.
    Przyjmuje:
    {
      "part_id": 1,
      "counter": 10,
      "is_empty": false
    }
    lub listę takich obiektów.
    """
    data = request.get_json(force=True)

    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400

    # --- Jeśli lista ---
    if isinstance(data, list):
        updated = 0
        for item in data:
            try:
                part_id = int(item["part_id"])
                counter = int(item["counter"])
                is_empty = bool(item["is_empty"])
                if repo.update_machine_part_stat(part_id, counter, is_empty):
                    updated += 1
            except (KeyError, ValueError, TypeError):
                continue
        return jsonify({"status": "ok", "updated": updated, "received": len(data)}), 200

    # --- Jeśli pojedynczy obiekt ---
    elif isinstance(data, dict):
        try:
            part_id = int(data["part_id"])
            counter = int(data["counter"])
            is_empty = bool(data["is_empty"])
        except (KeyError, ValueError, TypeError):
            return jsonify({"error": "Nieprawidłowe dane wejściowe"}), 400

        success = repo.update_machine_part_stat(part_id, counter, is_empty)
        if success:
            return jsonify({"status": "ok", "message": f"part_id={part_id} zaktualizowany"}), 200
        else:
            return jsonify({"error": f"Nie znaleziono części o part_id={part_id}"}), 404

    # --- Inny format ---
    else:
        return jsonify({"error": "Nieprawidłowy format JSON"}), 400
    
@app.route("/api/add_occurrences", methods=["POST"])
def api_add_occurrences():
    try:
        data = request.get_json()
        if not data or "alarms" not in data:
            return jsonify({"error": "Brak pola 'alarms' w JSON"}), 400

        alarms = data["alarms"]
        success = repo.insert_part_error_occurrences(alarms)
        if success:
            return jsonify({"status": "OK", "added": len(alarms)})
        else:
            return jsonify({"status": "FAIL"}), 500

    except Exception as e:
        print(f"❌ Błąd endpointu: {e}")
        return jsonify({"error": "Blad serwera"}), 500

    

    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
