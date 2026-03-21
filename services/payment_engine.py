import datetime


class PaymentEngine:

    def __init__(self):
        self._users = {}
        self._transactions = []
        self._transaction_no = 0

    # _users list/table->  amount
    # _transactions list/table->  transaction_id | user_id | amount | type(PAYMENT | REFUND) | status(SUCCESS | FAILED)| timestamp

    def reset(self):
        self._users.clear()
        self._transaction_no = 0
        self._transactions.clear()

    def _failed_status_msg(self, reason):
        return {
            'status': 'FAILED',
            'reason': reason
        }

    def _success_status_msg(self, balance, transaction_id=None):
        request_json = {
            'status': 'SUCCESS',
            'balance': balance,
        }
        if transaction_id:
            request_json['txn_id'] = transaction_id
        return request_json

    def _record_transaction(self, user_id: str, amount: float, txn_type: str, pay_txn_id=None):
        self._transaction_no += 1
        transaction_num = 'TXN_' + str(self._transaction_no)
        transaction = {
            'txn_id': transaction_num,
            'user_id': user_id,
            'amount': amount,
            'type': txn_type,
            'status': 'SUCCESS',
            'payment_txn_id': pay_txn_id,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        self._transactions.append(transaction)
        return transaction['txn_id']

    def convert_amount(self, amount):
        try:
            return float(amount)
        except (TypeError, ValueError):
            return None

    def check_user_exists(self, user_id):
        return user_id in self._users

    def create_user(self, user_id, amount):
        amount = self.convert_amount(amount)
        if self.check_user_exists(user_id):
            return self._failed_status_msg('USER_ALREADY_EXISTS')
        elif amount is None or amount < 0.00:
            return self._failed_status_msg('INVALID_AMOUNT')
        else:
            self._users[user_id] = amount
            return self._success_status_msg(self._users[user_id])

    def get_balance(self, user_id):
        if not self.check_user_exists(user_id):
            return self._failed_status_msg('USER_NOT_FOUND')
        else:
            return self._success_status_msg(self._users[user_id])

    def get_user_transactions(self, user_id: str):
        return [transaction for transaction in self._transactions if transaction['user_id'] == user_id]

    def get_transaction_types_for_id(self, user_id: str, transaction_id: str):
        transactions_list = list(transaction for transaction in self._transactions if transaction['user_id'] == user_id)
        return [transaction['type'] for transaction in transactions_list if transaction['txn_id'] == transaction_id]

    def check_if_payment_already_refunded(self, payment_txn_id: str):
        return any(
            t['payment_txn_id'] == payment_txn_id and t['type'] == 'REFUND'
            for t in self._transactions
        )

    def process_payment(self, user_id, amount):
        amount = self.convert_amount(amount)
        if amount is None or amount <= 0.00:
            return self._failed_status_msg('INVALID_AMOUNT')
        elif not self.check_user_exists(user_id):
            return self._failed_status_msg('USER_NOT_FOUND')
        elif amount > self._users[user_id]:
            return self._failed_status_msg('INSUFFICIENT_FUNDS')
        else:
            self._users[user_id] -= amount
            transaction_id = self._record_transaction(user_id, amount, 'PAYMENT', None)
            return self._success_status_msg(self._users[user_id], transaction_id)

    def refund_payment(self, user_id: str, amount: float | str | int, payment_txn_id: str):
        amount = self.convert_amount(amount)
        transactions = self.get_transaction_types_for_id(user_id, payment_txn_id)
        if amount is None or amount <= 0.00:
            return self._failed_status_msg('INVALID_AMOUNT')
        elif not self.check_user_exists(user_id):
            return self._failed_status_msg('USER_NOT_FOUND')
        elif not transactions:
            return self._failed_status_msg('INVALID_TRANSACTION_ID')
        elif self.check_if_payment_already_refunded(payment_txn_id):
            return self._failed_status_msg('PAYMENT_REFUND_COMPLETED')
        else:
            self._users[user_id] += amount
            self._record_transaction(user_id, amount, 'REFUND', payment_txn_id)
            return self._success_status_msg(self._users[user_id])
