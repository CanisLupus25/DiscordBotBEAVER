import numpy as np

arr = np.arange(16).reshape((4, 4))
print(np.roll(arr, (1, 0), axis=(1, 0)))