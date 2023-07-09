import os
import pandas as pd


def save_to_csv(df, filename):
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)
    else:
        df.to_csv(filename, mode='a', header=False, index=False)


filename = 'test_csv_append'

log_dict = {}
log_dict['status'] = 'error'
log_dict['l_zero'] = 3
log_dict['l_mult'] = 4

my_list = []
my_list.append(log_dict)

df = pd.DataFrame(my_list)

save_to_csv(df, filename)


log_dict = {}
log_dict['status'] = 'error'
log_dict['r_zero'] = 5
log_dict['r_mult'] = 6

my_list = []
my_list.append(log_dict)

df = pd.DataFrame(my_list)

save_to_csv(df, filename)