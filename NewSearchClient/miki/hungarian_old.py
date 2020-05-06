import sys

class Hungarian():
    
    def __init__(self):
        
        self.c_mat = None
        self.c_mat_orig = None
        self.row_count_orig = None
        self.col_count_orig = None
        self.n = None
    
    def prepare_mat(self, c_mat):
        
        row_count = len(c_mat)
        col_count = len(c_mat[0])
        self.c_mat_orig = c_mat
        self.row_count_orig = row_count
        self.col_count_orig = col_count
        
        
        c_mat = [[c_mat[i][j] for j in range(col_count)] for i in range(row_count)]
            
        diff = row_count - col_count
            
        if diff > 0:
            for i in range(row_count):
                c_mat[i] += [0 for j in range(diff)]
        elif diff < 0:
            new_cols = [[0 for i in range(col_count)] for j in range(-diff)]
            c_mat += new_cols
            
        self.c_mat = c_mat
        self.n = len(c_mat)
            
    def rc_max(self, row, col):
        
        vertical = 0
        horizontal = 0

        for i in range(self.n):
            if (self.c_mat[row][i] == 0):
                horizontal += 1

        for i in range(self.n):
            if (self.c_mat[i][col] == 0):
                vertical += 1

        if vertical > horizontal:
            return vertical
        else:
            return horizontal * -1
    
    @staticmethod
    def clear_neighbours(m2, m3, row, col):

        n = len(m2)

        if m2[row][col] > 0:
            for i in range(n):
                if m2[i][col] > 0:
                    m2[i][col] = 0
                m3[i][col] += 1
        else:
            for i in range(n):
                if (m2[row][i] < 0):
                    m2[row][i] = 0
                m3[row][i] += 1

        #m2[row][col] = 0
        #m3[row][col] = 1
    
    @staticmethod
    def print_mat(m):
        
        n = len(m)

        for row in range(n):
            string = ''
            for col in range(n):
                string += (str(m[row][col]) + '\t')
            print(string, file=sys.stderr, flush=True)
        print('\n', file=sys.stderr, flush=True)
        
    def cover_zeros(self):

        n = len(self.c_mat)

        m2 = [[0 for j in range(n)] for i in range(n)]
        m3 = [[0 for j in range(n)] for i in range(n)]

        for row in range(n):
            for col in range(n):
                if self.c_mat[row][col] == 0:
                    m2[row][col] = self.rc_max(row, col)

        #printMat(m2)

        for row in range(n):
            for col in range(n):
                if abs(m2[row][col]) > 0:
                    Hungarian.clear_neighbours(m2, m3, row, col)

        #printMat(m3)        
        return m3

    @staticmethod
    def get_line_count(m):
        
        n = len(m)
        
        if n == 1:
            return 1

        line_cnt = 0

        for col in range(n):
            is_column = True
            for row in range(n):
                if m[row][col] == 0:
                    is_column = False
                    break
            if not is_column:
                continue
            line_cnt += 1

        for row in range(n):
            is_row = True
            for col in range(n):
                if m[row][col] == 0:
                    is_row = False
                    break
            if not is_row:
                continue
            line_cnt += 1

            
        if line_cnt > n:
            return n
        
        return line_cnt

    @staticmethod
    def find_min(c_mat, mask=None):
        
        #Hungarian.print_mat(c_mat)
        
        row_count = len(c_mat)
        col_count = len(c_mat[0])

        min_elem = float('inf')
        
        if mask is not None:
            for i in range(row_count):
                for j in range(col_count):
                    if mask[i][j]:
                        continue
                    if c_mat[i][j] < min_elem:
                        min_elem = c_mat[i][j]
                        min_pos = (i, j)
        else:
            for i in range(row_count):
                for j in range(col_count):
                    if c_mat[i][j] < min_elem:
                        min_elem = c_mat[i][j]
                        min_pos = (i, j)

        return min_pos
    
    def solve(self, c_mat):
        # Solves a given assignment problem provided
        # by c_mat, and populates the instance variables
        # for further analysis.
        
        self.prepare_mat(c_mat)
        
        for i in range(self.n):
            row_min = float('inf')
            for j in range(self.n):
                if self.c_mat[i][j] < row_min:
                    row_min = self.c_mat[i][j]
            for j in range(self.n):
                self.c_mat[i][j] -= row_min

        for i in range(self.n):
            col_min = float('inf')
            for j in range(self.n):
                if self.c_mat[j][i] < col_min:
                    col_min = self.c_mat[j][i]
            for j in range(self.n):
                self.c_mat[j][i] -= col_min

        lines = self.cover_zeros()
        line_count = Hungarian.get_line_count(lines)

        if line_count == self.n:
            return self.c_mat

        while (line_count != self.n):
            min_idx = Hungarian.find_min(self.c_mat, mask=lines)
            min_elem = self.c_mat[min_idx[0]][min_idx[1]]

            for i in range(self.n):
                for j in range(self.n):
                    self.c_mat[i][j] += min_elem * (lines[i][j] - 1)

            lines = self.cover_zeros()
            line_count = Hungarian.get_line_count(lines)

        return c_mat
    
    def get_min_cost(self):
        # Returns the distance cost of the minimum cost matching
        
        cost = 0
        
        for i in range(self.row_count_orig):
            for j in range(self.col_count_orig):
                if self.c_mat[i][j] == 0:
                    cost += self.c_mat_orig[i][j]
                    continue
        return cost
    
    def get_assignments(self):
        # Returns assignments in an array of tuples, where each tuple
        # corresponds to an assignment in a (row, col, distance) format.
        
        assignments = []
        
        for i in range(self.row_count_orig):
            for j in range(self.col_count_orig):
                if self.c_mat[i][j] == 0:
                    assignments.append((i, j, self.c_mat_orig[i][j]))
                    
        return assignments