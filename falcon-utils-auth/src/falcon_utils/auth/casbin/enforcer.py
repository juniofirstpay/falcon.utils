from casbin import Enforcer
from .adapter import FileAdapter

__all__ = ("create_enforcer",)


def create_enforcer(model_path, policy_path, logging=False) -> Enforcer:
    return Enforcer(model_path, FileAdapter(policy_path), enable_log=logging)
