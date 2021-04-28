def ascii_to_bits(c):
    result = []
    bits = bin(ord(c))[2:]
    bits = '00000000'[len(bits):] + bits
    result.extend([int(bit) for bit in bits])
    return result

def bits_to_ascii(bits):
    return chr(int(''.join([str(bit) for bit in bits]), 2))

def int_to_bits(n):
    result = []
    bits = bin(n)[2:]
    bits = '00000000'[len(bits):] + bits
    result.extend([int(bit) for bit in bits])
    return result

def bits_to_int(bits):
    return int(''.join([str(bit) for bit in bits]), 2)

def hide_3bits_in_pixel(original_pixel, bit_1, bit_2, bit_3):
    r, g, b = original_pixel
    new_r = (r&254) + bit_1
    new_g = (g&254) + bit_2
    new_b = (b&254) + bit_3
    return (new_r, new_g, new_b)

def hide_2bits_in_pixel(original_pixel, bit_1, bit_2):
    r, g, b = original_pixel
    r = (r&254) + bit_1
    g = (g&254) + bit_2
    return (r, g, b)

def hide_1byte_in_9pixels(loader, bits):
    cordinate = loader.next_pixel_cordinate()
    tmp = loader.get_pixel_at(cordinate)
    new_pixel = hide_3bits_in_pixel(tmp, bits[0], bits[1], bits[2])
    loader.edit_pixel_at(cordinate, new_pixel)

    cordinate = loader.next_pixel_cordinate()
    tmp = loader.get_pixel_at(cordinate)
    new_pixel = hide_3bits_in_pixel(tmp, bits[3], bits[4], bits[5])
    loader.edit_pixel_at(cordinate, new_pixel)
    
    cordinate = loader.next_pixel_cordinate()
    tmp = loader.get_pixel_at(cordinate)
    new_pixel = hide_2bits_in_pixel(tmp, bits[6], bits[7])
    loader.edit_pixel_at(cordinate, new_pixel)

def extract_hex_from_pixels(pixels):
    color_values = [value for pixel in pixels for value in pixel]
    bits = []
    for i in range(8):
        bits.append(int_to_bits(color_values[i])[7])
    return bits_to_int(bits)

def extract_ascii_from_pixels(pixels):
    bits = []
    values = [value for pixel in pixels for value in pixel] 
    for i in range(8):
        bits.append(int_to_bits(values[i])[7])
    return (bits_to_ascii(bits))

def extract_int(loader, delim):
    c_list = []
    while True:
        pixels = []
        for i in range(3):
            cordinate = loader.next_pixel_cordinate()
            pixels.append(loader.get_pixel_at(cordinate))
        c = extract_ascii_from_pixels(pixels)
        if c == delim:
            break
        c_list.append(c)
    return int(''.join(c_list))

def extract_hex_stream(loader, len):
    hex_list = []
    for i in range(len):
        pixels = []
        for i in range(3):
            cordinate = loader.next_pixel_cordinate()
            pixels.append(loader.get_pixel_at(cordinate))
        hex_value = extract_hex_from_pixels(pixels)
        hex_list.append(hex_value)
    return hex_list

