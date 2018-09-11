# to compute matrix multiplication for part 3 of question 1
import numpy as np
from numpy.linalg import matrix_power
i = np.array([[0.00, 0.40, 0.00, 0.60], [0.70, 0.00, 0.30, 0.00], [0.00, 0.80, 0.00, 0.20], [0.10, 0.90, 0.00, 0.00]]) 
print(np.matmul([1,0,0,0], matrix_power(i, 50)))
