from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from datetime import datetime
from flask import Response, stream_with_context
import json, time
from datetime import datetime, timedelta
from queue import Queue,Empty
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
sse_queue = Queue()  # globalna kolejka do SSE

# ------------------ USERS (do testu logowania) ------------------
USERS = {
    "admin": "password123"
}

# ------------------ helper get_payload ------------------
def get_payload(machine_id: int = 1):
    """
    Zwraca serializowalny payload dla danej maszyny.
    Pobiera:
      - last_errors (lista DTO)
      - error_str (kody błędów dla pierwszej części, z ostatniej minuty)
      - counters (statystyki części)
      - parts (lista części, przydatne dla frontu)
      - timestamp
    Wszystko przechodzi przez to_primitive(), więc json.dumps zadziała.
    """
    try:
        # ustawienia domyślne
        last_min = datetime.now() - timedelta(days=30)

        # pobieramy części i counters
        parts_raw = repo.get_machine_parts_by_machine_id(machine_id)
        counters_raw = repo.get_stats_for_machine(machine_id)

        # last errors z repo (DTO)
        last_errors_raw = repo.get_last_errors(machine_id)

        # wybieramy part_id do query error_str (jeśli nie ma części, użyj 1)
        part_id = None
        if parts_raw and isinstance(parts_raw, (list, tuple)) and len(parts_raw) > 0:
            # obiekt części może mieć atrybut id lub property 'id'
            first = parts_raw[0]
            part_id = getattr(first, "id", None) or getattr(first, "part_id", None) or None

        if part_id is None:
            part_id = 1

        machine_id=1;    

        # pobieramy error_str (kody) od last_min
        error_str_raw = repo.get_error_code_for_machine_in_date_range(machine_id, date_from=last_min)

        # konwersja na prymitywy
        payload = {
            "timestamp": datetime.now().isoformat(),
            "machine_id": machine_id,
            "parts": to_primitive(parts_raw),
            "counters": to_primitive(counters_raw),
            "last_errors": to_primitive(last_errors_raw),
            "error_str": to_primitive(error_str_raw),
        }
        return payload

    except Exception as e:
        # jeśli coś pójdzie nie tak, zwracamy komunikat błędu, ale strumień nie upada
        print(f"❌ Błąd w get_payload(): {e}")
        return {"timestamp": datetime.now().isoformat(), "error": "get_payload_failed", "msg": str(e)}

def to_primitive(obj):
    # proste typy
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # datetime -> ISO string
    if isinstance(obj, datetime):
        return obj.isoformat()

    # listy/tuple -> rekurencja
    if isinstance(obj, (list, tuple)):
        return [to_primitive(i) for i in obj]

    # słowniki -> rekurencja po wartościach
    if isinstance(obj, dict):
        return {k: to_primitive(v) for k, v in obj.items()}

    # obiekty mające to_dict()
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        try:
            data = obj.to_dict()
            return to_primitive(data)
        except Exception:
            pass

    # obiekty z __dict__ (np. DTO)
    if hasattr(obj, "__dict__"):
        try:
            data = vars(obj)
            return {k: to_primitive(v) for k, v in data.items()}
        except Exception:
            pass

    # fallback: string representation
    try:
        return str(obj)
    except Exception:
        return None




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
        sse_queue.put(True) 
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
            sse_queue.put(True) 
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
            sse_queue.put(True) 
            return jsonify({"status": "OK", "added": len(alarms)})
        else:
            return jsonify({"status": "FAIL"}), 500

    except Exception as e:
        print(f"❌ Błąd endpointu: {e}")
        return jsonify({"error": "Blad serwera"}), 500
    
@app.route("/api/stream")
def sse_stream():
    def generate():
        # pobieramy machine_id z query params (np. /api/stream?machine_id=2)
        try:
            req_machine_id = int(request.args.get("machine_id") or 1)
        except Exception:
            req_machine_id = 1

        while True:
            try:
                # czeka maksymalnie 60s na sygnał z POST; jeśli nic, to wyśle snapshot
                sse_queue.get(timeout=5)
            except Empty:
                # timeout – brak zmian, i tak wyśle snapshot
                pass

            try:
                payload = get_payload(machine_id=req_machine_id)
                yield f"data: {json.dumps(payload)}\n\n"
            except Exception as e:
                # logujemy i wysyłamy informację o błędzie (ale nie zamykamy strumienia)
                print(f"❌ Błąd w serializacji SSE: {e}")
                try:
                    err_payload = {"timestamp": datetime.now().isoformat(), "error": "serialization_error", "msg": str(e)}
                    yield f"data: {json.dumps(err_payload)}\n\n"
                except Exception:
                    # jeśli nawet to się nie powiedzie, czekamy chwilę i kontynuujemy
                    time.sleep(1)

    return Response(stream_with_context(generate()), mimetype="text/event-stream")
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
