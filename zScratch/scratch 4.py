import numpy as np


my_array = [0.0, -1.0, -1.5, -2.0, -3.0, -4.0]
np_array = np.array(my_array)

velocity_min_index = 5

velocity_zero_index = np.where(np_array[velocity_min_index:] > 0)
print(f'velocity_zero_index {velocity_zero_index}, len of tuple: {len(velocity_zero_index)}')

velocity_zero_index = velocity_zero_index[0][0]
print(velocity_zero_index)