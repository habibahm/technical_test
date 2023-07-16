import operator
from backend.logic import transactions
from backend.models.interfaces import Database


def current_balance(db: Database, user_id: int) -> int:
    """
    Returns current balance of the user
    """
    user_transactions = transactions.transactions(db, user_id)
    current_balance = 0
    for transaction in user_transactions:
        if transaction.type == "deposit" and transaction.state == "completed":
            current_balance += transaction.amount
        if (
            transaction.type == "scheduled_withdrawal"
            and transaction.state == "completed"
        ):
            current_balance -= transaction.amount
        if transaction.type == "refund" and transaction.state in [
            "completed",
            "pending",
        ]:
            current_balance -= transaction.amount
    return current_balance


def future_balance(db: Database, user_id: int) -> list:
    """
    Returns dict with the future balance of the user and the future withdrawals
    """
    scheduled_withdrawals = [
        transaction
        for transaction in db.scan("transactions")
        if transaction.user_id == user_id
        and transaction.type == "scheduled_withdrawal"
        and transaction.state == "scheduled"
    ]
    sorted_withdrawals = sorted(scheduled_withdrawals, key=operator.attrgetter("date"))
    future_withdrawals = [
        {
            "withdrawal": withdrawal.id,
            "amount": withdrawal.amount,
            "covered_amount": 0,
            "covered_rate": 0,
        }
        for withdrawal in sorted_withdrawals
    ]
    i = 0
    balance = current_balance(db, user_id)
    while balance > 0 and i < len(sorted_withdrawals):
        withdrawal = sorted_withdrawals[i]
        covered_amount = min(withdrawal.amount, balance)
        covered_rate = covered_amount * 100 / withdrawal.amount
        balance -= covered_amount
        future_withdrawals[i]["covered_amount"] = covered_amount
        future_withdrawals[i]["covered_rate"] = covered_rate
        i += 1
    return {"balance": balance, "future_withdrawals": future_withdrawals}
