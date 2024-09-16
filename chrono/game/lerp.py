def clamp(min_val, val, mav_val):
    """Clamp a `val` to be no lower than `minVal`, and no higher than `maxVal`."""
    return max(min_val, min(mav_val, val))

def perc(start: float, end: float, curr: float) -> float:
    """Convert a number to its progress through the range start -> end, from 0 to 1.

    https://www.desmos.com/calculator/d2qdk3lceh"""
    if end - start <= 0:
        return 1 if curr >= start else 0
    duration = end - start
    p = (curr - start) / duration
    return clamp(0, p, 1)


def lerp(start: float, end: float, i: float) -> float:
    """Convert a number between 0 and 1 to be the progress within a range start -> end."""
    return start + (i * (end - start))

