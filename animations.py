import math


def ease_out_bounce(t):
    """弹跳缓动函数"""
    if t < 0.36:
        return 7.5625 * t * t
    elif t < 0.73:
        t -= 0.545
        return 7.5625 * t * t + 0.75
    elif t < 0.91:
        t -= 0.819
        return 7.5625 * t * t + 0.9375
    else:
        t -= 0.955
        return 7.5625 * t * t + 0.984375


def ease_out_elastic(t):
    """弹性缓动函数"""
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


def ease_in_out_quad(t):
    """二次缓动函数"""
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
