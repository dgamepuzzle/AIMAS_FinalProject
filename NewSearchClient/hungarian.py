import copy
NONE, STARRED, PRIMED = 0, 1, 2

def hungarian(c_mat):
    
    row_count = len(c_mat)
    col_count = len(c_mat[0])

    return [elem for elem in minimize(prepare_mat(c_mat)) if elem[0] < row_count and elem[1] < col_count]

def minimize(c_mat):

    c_mat = copy.deepcopy(c_mat)
    n = len(c_mat)

    for row in c_mat:
        m = min(row)
        if m != 0:
            row[:] = map(lambda x: x - m, row)

    mask_mat = [[NONE] * n for _ in c_mat]
    row_cover = [False] * n
    col_cover = [False] * n

    for r, row in enumerate(c_mat):
        for c, value in enumerate(row):
            if value == 0 and not row_cover[r] and not col_cover[c]:
                mask_mat[r][c] = STARRED
                row_cover[r] = True
                col_cover[c] = True

    row_cover = [False] * n
    col_cover = [False] * n

    match_found = False

    while not match_found:
        for i in range(n):
            col_cover[i] = any(mrow[i] == STARRED for mrow in mask_mat)

        if all(col_cover):
            match_found = True
            continue
        else:
            zero = cover_zeros(c_mat, mask_mat, row_cover, col_cover)

            primes = [zero]
            stars = []
            while zero:
                zero = find_star_in_col(mask_mat, zero[1])
                if zero:
                    stars.append(zero)
                    zero = find_prime_in_row(mask_mat, zero[0])
                    stars.append(zero)

            for star in stars:
                mask_mat[star[0]][star[1]] = NONE

            for prime in primes:
                mask_mat[prime[0]][prime[1]] = STARRED

            for r, row in enumerate(mask_mat):
                for c, val in enumerate(row):
                    if val == PRIMED:
                        mask_mat[r][c] = NONE

            row_cover = [False] * n
            col_cover = [False] * n

    solution = []
    for r, row in enumerate(mask_mat):
        for c, val in enumerate(row):
            if val == STARRED:
                solution.append((r, c))
    return solution

def prepare_mat(c_mat):
    row_count = len(c_mat)
    col_count = len(c_mat[0])

    c_mat = [[c_mat[i][j] for j in range(col_count)] for i in range(row_count)]

    diff = row_count - col_count

    if diff > 0:
        for i in range(row_count):
            c_mat[i] += [0 for j in range(diff)]
    elif diff < 0:
        new_cols = [[0 for i in range(col_count)] for j in range(-diff)]
        c_mat += new_cols
        
    return c_mat        

def cover_zeros(c_mat, mask_mat, row_cover, col_cover):

    while True:
        zero = True

        while zero:
            zero = find_noncovered_zero(c_mat, row_cover, col_cover)
            if not zero:
                break
            else:
                row = mask_mat[zero[0]]
                row[zero[1]] = PRIMED

                try:
                    index = row.index(STARRED)
                except ValueError:
                    return zero

                row_cover[zero[0]] = True
                col_cover[index] = False

        m = min(uncovered_values(c_mat, row_cover, col_cover))
        for r, row in enumerate(c_mat):
            for c, __ in enumerate(row):
                if row_cover[r]:
                    c_mat[r][c] += m
                if not col_cover[c]:
                    c_mat[r][c] -= m


def find_noncovered_zero(c_mat, row_cover, col_cover):
    for r, row in enumerate(c_mat):
        for c, value in enumerate(row):
            if value == 0 and not row_cover[r] and not col_cover[c]:
                return (r, c)
    else:
        return None


def uncovered_values(c_mat, row_cover, col_cover):
    for r, row in enumerate(c_mat):
        for c, value in enumerate(row):
            if not row_cover[r] and not col_cover[c]:
                yield value


def find_star_in_col(mask_mat, c):
    for r, row in enumerate(mask_mat):
        if row[c] == STARRED:
            return (r, c)
    else:
        return None


def find_prime_in_row(mask_mat, r):
    for c, val in enumerate(mask_mat[r]):
        if val == PRIMED:
            return (r, c)
    else:
        return None