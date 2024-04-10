mode = 0
manual_select = 1
channel = 13

numb = (channel << 5) + (manual_select << 1) + mode


def binary_with_underscore(n):
    binary = format(n, 'b')
    reversed_binary = binary[::-1]
    underscored = ''.join([reversed_binary[i] + ('_' if (i+1) % 4 == 0 else '') for i in range(len(reversed_binary))])
    return underscored[::-1]

# Test the function

print(binary_with_underscore(numb))
