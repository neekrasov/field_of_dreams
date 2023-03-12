from .types import Controller


def admin_required(handler: Controller):
    setattr(handler, "admin_required", True)
    return handler
