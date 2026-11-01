from flask import Flask, jsonify, request, send_from_directory
import os
from db import (
    get_all_equipment,
    get_all_technicians,
    get_all_requests,
    get_request_by_id,
    create_request,
    add_update,
    get_updates_for_request,
    update_request_status_with_history,
)

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Equipment endpoints
@app.route('/api/equipment')
def api_equipment():
    return jsonify(get_all_equipment())

# Technicians endpoints
@app.route('/api/technicians')
def api_technicians():
    return jsonify(get_all_technicians())

# Service requests endpoints
@app.route('/api/requests')
def api_requests():
    return jsonify(get_all_requests())

@app.route('/api/request/<int:req_id>')
def api_request_detail(req_id):
    req = get_request_by_id(req_id)
    if not req:
        return jsonify({'error': 'Not found'}), 404
    req['updates'] = get_updates_for_request(req_id)
    return jsonify(req)

@app.route('/api/request', methods=['POST'])
def api_create_request():
    data = request.json
    create_request(
        data['equipment_id'],
        data['technician_id'],
        data.get('description', ''),
        data.get('status', 'OPEN')
    )
    return jsonify({'status': 'created'}), 201

@app.route('/api/request/<int:req_id>/status', methods=['POST'])
def api_update_status(req_id):
    data = request.json
    try:
        update_request_status_with_history(
            req_id,
            data['new_status'],
            data['technician_id'],
            data.get('note', '')
        )
        return jsonify({'status': 'updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Ensure DB exists
    if not os.path.exists('maintenance.db'):
        print('Database missing – run schema.sql and populate_data.py first')
    app.run(debug=True)
