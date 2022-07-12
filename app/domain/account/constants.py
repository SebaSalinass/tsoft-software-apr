from enum import IntEnum


class AccountState(IntEnum):

    ACTIVE = 1
    CUT_IN_PROCESS = 2
    WATER_CUT = 3
    DISABLED = 4


class SubsidyType(IntEnum):

    NONE = 0
    AMOUNT = 1
    PERCENTAGE = 2