from enum import Enum


class ExceptionEnum(Enum):
    SUCCESS = ("0000", "OK")
    FAILED = ("9999", "系统异常")
    USER_NO_DATA = ("10001", "用户数据不存在")
    USER_REGISTER_ERROR = ("10002", "用户注册失败")
    PERMISSIONS_ERROR = ("20001", "没有操作权限")


class BusinessError(Exception):
    __slots__ = ["err_code", "err_code_des"]
    def __init__(self, result: ExceptionEnum = None, err_code: str = "00000", err_code_des: str = ""):
        if result:
            self.err_code = result.value[0]
            self.err_code_des = err_code_des or result.value[1]
        else:
            self.err_code = err_code
            self.err_code_des = err_code_des
        super().__init__(self)

