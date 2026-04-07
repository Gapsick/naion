class ToolError(Exception):
    """모든 툴 에러의 베이스"""
    pass


class ToolInputError(ToolError):
    """Claude가 잘못된 인자를 보냈을 때 (KeyError, TypeError 등)"""
    pass


class ToolExecutionError(ToolError):
    """툴 실행 중 예상치 못한 에러"""
    pass
