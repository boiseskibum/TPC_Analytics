total_elements = 4  # T - Total number of elements
current_element_index = 0  # CE - Current element index (0-based)

# Each page holds 4 elements
elements_per_page = 4

# Calculate total number of pages
# We use ceil to round up because even a single element requires a whole page
total_pages = -(-total_elements // elements_per_page)  # Equivalent to math.ceil(total_elements / elements_per_page)

# Calculate current page
# We add 1 because we're counting pages from 1, but elements are 0-indexed
current_page = (current_element_index // elements_per_page) + 1

# Create the string
page_info = f"page {current_page} of {total_pages}"

print(page_info)
