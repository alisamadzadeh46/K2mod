from django.conf import settings


def client_ip(request):
    # nginx puts the real address in X-Real-IP, REMOTE_ADDR is the proxy
    if settings.BEHIND_PROXY:
        ip = request.META.get("HTTP_X_REAL_IP")
        if ip:
            return ip
    return request.META.get("REMOTE_ADDR")
