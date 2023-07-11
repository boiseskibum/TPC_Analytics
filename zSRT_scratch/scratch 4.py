data = []

data.append((1, 2))
data.append((3, 4))

print(f"type of data; {type( (1,2) )}")
print(f"type of data; {type(data)}")
for row in data:
    product = row[0] * row[1]
    row.append(product)

print(data)