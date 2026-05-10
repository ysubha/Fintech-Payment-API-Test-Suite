from flask import Flask, jsonify, request
from services.payment_engine import PaymentEngine

api = Flask(__name__)
pay_engine = PaymentEngine()
idempotency_store = {}

if __name__ == '__main__':
    api.run(port=5000, debug=True)


@api.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    if (not user_data) or ('user_id' not in user_data) or ('amount' not in user_data):
        return jsonify({
            'status': 'FAILED',
            'reason': 'INVALID_INPUT'

        }), 400

    response = pay_engine.create_user(user_data['user_id'], user_data['amount'])
    if response['status'] == 'SUCCESS':
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@api.route('/payments', methods=['POST'])
def process_payment():
    payment_data = request.json
    if (not payment_data) or ('user_id' not in payment_data) or ('amount' not in payment_data):
        return jsonify({
            'status': 'FAILED',
            'reason': 'INVALID_INPUT'
        }), 400
    else:
        idempotency_key = request.headers.get('Idempotency-key')
        if idempotency_key and idempotency_key in idempotency_store:
            response = idempotency_store[idempotency_key]
        else:
            response = pay_engine.process_payment(payment_data['user_id'], payment_data['amount'])
            if idempotency_key:
                idempotency_store[idempotency_key] = response
        if response['status'] == 'SUCCESS':
            return jsonify(response), 200
        else:
            return jsonify(response), 400


@api.route('/users/<string:user_id>/balance', methods=['GET'])
def get_balance(user_id):
    balance_json_data = pay_engine.get_balance(user_id)
    if balance_json_data['status'] == 'FAILED':
        return jsonify(balance_json_data), 400
    else:
        return jsonify(balance_json_data), 200


@api.route('/users/<string:user_id>/transactions', methods=['GET'])
def get_user_transactions(user_id):
    if not pay_engine.check_user_exists(user_id):
        return jsonify({'status': 'FAILED', 'reason': 'USER_NOT_FOUND'}), 400
    return jsonify(pay_engine.get_user_transactions(user_id)), 200


@api.route('/refunds', methods=['POST'])
def refund_payment():
    refund_json_data = request.json
    if not refund_json_data or 'user_id' not in refund_json_data or 'amount' not in refund_json_data or 'txn_id' not in refund_json_data:
        return jsonify({
            'status': 'FAILED',
            'reason': 'INVALID_INPUT'
        }), 400
    response = pay_engine.refund_payment(refund_json_data['user_id'], refund_json_data['amount'],
                                         refund_json_data['txn_id'])
    if response['status'] == 'SUCCESS':
        return jsonify(response), 200
    else:
        return jsonify(response), 400
