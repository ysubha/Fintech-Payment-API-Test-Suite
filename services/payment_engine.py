
class PaymentEngine:

    def __init__(self):
        self._users = {}

    def _failed_status_msg(self,reason):
        return {
            "status": "FAILED",
            "reason": reason
        }

    def _success_status_msg(self,balance):
        return {
            "status": "SUCCESS",
            "balance": balance
        }

    def convert_amount (self, amount):
        try:
            return float(amount)
        except (TypeError,ValueError):
            return None

    def check_user_exists(self, user_id):
        return user_id in self._users

    def create_user(self, user_id, amount):
        amount = self.convert_amount(amount)
        if self.check_user_exists(user_id):
            return self._failed_status_msg("USER_ALREADY_EXISTS")
        elif amount is None or amount < 0.00:
            return self._failed_status_msg("INVALID_AMOUNT")
        else:
            self._users[user_id] = amount
            return self._success_status_msg(self._users[user_id])

    def get_balance(self,user_id):
        if not self.check_user_exists(user_id):
            return self._failed_status_msg("USER_NOT_FOUND")
        else:
            return self._success_status_msg(self._users[user_id])

    def process_payment(self,user_id, amount):
        amount = self.convert_amount(amount)
        if amount is None or amount <= 0.00:
            return self._failed_status_msg("INVALID_AMOUNT")
        elif not self.check_user_exists(user_id):
            return self._failed_status_msg("USER_NOT_FOUND")
        elif amount > self._users[user_id]:
            return self._failed_status_msg("INSUFFICIENT_FUNDS")
        else:
            self._users[user_id] -= amount
            return self._success_status_msg(self._users[user_id])

    def refund_payment(self,user_id, amount):
        amount = self.convert_amount(amount)
        if amount is None or amount <= 0.00:
            return self._failed_status_msg("INVALID_AMOUNT")
        elif not self.check_user_exists(user_id):
            return self._failed_status_msg("USER_NOT_FOUND")
        else:
            self._users[user_id] += amount
            return self._success_status_msg(self._users[user_id])