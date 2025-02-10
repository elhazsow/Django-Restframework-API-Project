from rest_framework.throttling import UserRateThrottle

class RateThrottle(UserRateThrottle):
    rate = '50/min'