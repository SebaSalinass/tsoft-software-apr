from enum import IntEnum


class Permission(IntEnum):
    
    READ = 1
    WRITE_NEWS = 2
    MANAGE_INVENTORY = 4
    MANAGE_USERS = 8
    MANAGE_ACCOUNTS = 16
    MANAGE_SERVICE = 32
    MANAGE_BALANCE = 64
    ADMIN = 128
