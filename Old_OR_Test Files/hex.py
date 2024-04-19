# mode = 0
# manual_select = 1
# channel = 13

# numb = (channel << 5) + (manual_select << 1) + mode


# def binary_with_underscore(n):
#     binary = format(n, 'b')
#     reversed_binary = binary[::-1]
#     underscored = ''.join([reversed_binary[i] + ('_' if (i+1) % 4 == 0 else '') for i in range(len(reversed_binary))])
#     return underscored[::-1]

# # Test the function

# print(binary_with_underscore(numb))

# Assuming self.mode is an integer
self_mode = 160  # Example value

# Perform right shift operation by 5 bits and bitwise AND operation with 15
result = ((self_mode >> 5) & 15) + 1

# Print the result
print("Result:" + str(((self_mode >> 5) & 15) + 1))
