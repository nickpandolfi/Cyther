from math import sqrt


cdef int triangular(int n):
    cdef:
        double q
        int r
    q = (n * (n + 1)) / 2
    r = int(q)
    return r


def inverse_triangular(n):
    x = (sqrt(8 * n + 1) - 1) / 2
    n = int(x)
    if x - n > 0:
        return False
    return int(x)