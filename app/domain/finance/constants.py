from enum import IntEnum

class TransactionType(IntEnum):
    CASH = 1
    TRANSFER = 2
    WEBPAY = 3
    OTHER = 4


class ChargeState(IntEnum):
    PENDING = 0
    OVERDUE = 1
    COMPLETED = 2
    NULLED = 3
    RENEGOTIATED = 4


class InstallmentState(IntEnum):
    PENDING = 0
    COMPLETED = 1
    EXPIRED = 2


class RenegotiationState(IntEnum):

    PENDING = 0
    UP_TO_DATE = 1
    OVERDUE = 2
    COMPLETED = 3
