from .gateways import ManualPendingGateway

# TODO: online gateway
_ACTIVE_GATEWAY = ManualPendingGateway()


def get_active_gateway():
    return _ACTIVE_GATEWAY
