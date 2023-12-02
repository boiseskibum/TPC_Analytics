# this function filters down values based upon the following rules
#       replaces -4000000's with with prior good values or if necessary the next good value
#       replaces -101 values with prior good values or if necessary the next good value

def clean_column_values(column):
    ugly_value = -4000000

    for i in range(len(column)):
        if column[i] == -101 or column[i] < ugly_value:
            if i > 0:
                column[i] = column[i - 1]
            else:  # handle the case at the beginning of a string  - ie find the first non error value but don't try
                    # more than 10 spots out
                k_max = 10
                if len(column) < 10:
                    k_max = len(column)
                for j in range(i, k_max):
                    if column[j] != -101 and column[j] > ugly_value:
                        column[i] = column [j]
                        break
    return column



# Example usage

print (f"\ntest case 1 - general")
my_list = [22, -101 , -101, 20, 25, 30, 33, -101, 44, -101, 1, 2, 3]
print(my_list)
clean_column_values(my_list)
print(my_list)

print (f"\ntest case 2 - first and last values")
my_list = [-101, -101 , -101, 44, 25, 30, 33, -101, 44, -101, 1, 2, 3]
print(my_list)
clean_column_values(my_list)
print(my_list)

print (f"\ntest case 3 - -4289123 cases")
my_list = [22, -4289123, -101, 24, 25, 30, 40, -101, 33, -101, 44, -4289123, -101]
print(my_list)
clean_column_values(my_list)
print(my_list)

print (f"\ntest case 4 - -4289123 cases")
my_list = [-4289123, -101, 22, 25, 30, 33, -101, 44, -101, 55, -4289123, -101]
print(my_list)
clean_column_values(my_list)
print(my_list)

print (f"\ntest case 4 - -4289123 cases")
my_list = [-101, -101, -101, -101,-101, -101, -101, -101, -101, -101, -101, -101, -101, -101, -101, -101, -101, -101, -101,]
print(my_list)
clean_column_values(my_list)
print(my_list)
