#!/usr/bin/env python3
import sys
sys.path.insert(1, 'module')

from des import DesKey
from dcutils import *
from dcimage import *
import argparse
import ntpath

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def create_stego_image(cover_img_path, secret_img_path, output_path, password):
    # load both cover and secret image
    obj = PixelLoader(cover_img_path)
    obj2 = PixelLoader(secret_img_path)
  
    # craft header data
    filename = path_leaf(secret_img_path)
    dimension = obj2.get_dimension()
    header = filename + " " + str(dimension[0]) + " " + str(dimension[1]) + " "
    header_len = len(header)
    if header_len % 8 != 0:
        header_len += 8 - header_len%8

    # check cover image have sufficient space for hidding
    cover_d = obj.get_dimension()
    cover_size = cover_d[0]*cover_d[1]
    required_pixels = (dimension[0]*dimension[1]) * 9 + (header_len + 1) * 3
    if cover_size < required_pixels:
        print("Error: Insufficient cover img size")
        print("Cover img size: " + str(cover_size))
        print("Required size: >=" + str(required_pixels))
        sys.exit()

    # generate DES key
    key = DesKey(bytes(password, "utf-8"))
    
    # encrypt header data
    arry = []
    for c in header:
        arry.append(ord(c))
    cypher_text = key.encrypt(bytes(arry), padding=True).hex()
    encrypted_header = [cypher_text[i:i+2] for i in range(0, len(cypher_text), 2)]
    
    for c in str(header_len) + " ":
        hide_1byte_in_9pixels(obj, ascii_to_bits(c))        
    for hex_string in encrypted_header:
        hide_1byte_in_9pixels(obj, int_to_bits(int(hex_string, 16)))          

    # encrypt image data
    data_arry = obj2.to_int_arry()
    cypher_text = key.encrypt(bytes(data_arry), padding=True).hex()
    encrypted_rgb = [cypher_text[i:i+2] for i in range(0, len(cypher_text), 2)]
    for hex_string in encrypted_rgb:
        hide_1byte_in_9pixels(obj, int_to_bits(int(hex_string, 16)))          

    # save the stego image
    obj.save(output_path)
    print("-> success!")

def extract_secret_image(stego_img, password):
    obj3 = PixelLoader(stego_img)

    # create DES key from password
    key = DesKey(bytes(password, "utf-8"))
    # extract/decrypt header information
    header_len = extract_int(obj3, " ")
    hex_arry = extract_hex_stream(obj3, header_len)
    decrypted_header = key.decrypt(bytes(hex_arry)).hex()
    decrypted_header = [decrypted_header[i:i+2] for i in range(0, len(decrypted_header), 2)]
    header = []
    for hex_string in decrypted_header:
        header.append(chr(int(hex_string, 16)))
    header = ''.join(header)

    header_info = header.split(" ")
    if len(header_info) != 4:
        print("Error: password invalid")
        sys.exit()

    filename = header_info[0]
    row_n = int(header_info[1])
    col_n = int(header_info[2])

    # extract image
    secret_img = Image.new('RGB', (row_n, col_n))

    n = (row_n * col_n) * 3
    if n % 8 != 0:
        n += 8 - (n % 8)

    values = []
    for i in range(n): 
        pixels = []
        for j in range(3):
            cordinate = obj3.next_pixel_cordinate()
            pixels.append(obj3.get_pixel_at(cordinate))
        values.append(extract_hex_from_pixels(pixels))

    # decrypt RGB values
    key = DesKey(bytes(password, "utf-8"))
    decrypted_rgb = key.decrypt(bytes(values)).hex()
    decrypted_rgb = [decrypted_rgb[i:i+2] for i in range(0, len(decrypted_rgb), 2)]

    index = 0
    for row in range(row_n):
        for col in range(col_n):
            r = int(decrypted_rgb[index], 16)
            index += 1
            g = int(decrypted_rgb[index], 16)
            index += 1
            b = int(decrypted_rgb[index], 16) 
            index += 1
            secret_img.putpixel((row, col), (r,g,b))
    secret_img.save(filename)
    print("-> success!")

def factor_passwd(passwd):
    length = len(passwd)
    if length > 24:
        print("Error: Invalid password length")
        print("Password must be of length < 24")
        sys.exit()
    if length <= 8 and length%8 != 0:
        passwd = "{:<8}".format(passwd)
    elif length <= 16 and length%8 != 0:
        passwd = "{:<16}".format(passwd)
    else:
        passwd = "{:<24}".format(passwd)
    return passwd

def check_extension(filename):
    if not filename.endswith('.bmp'):
        print("Erro: Invalid file extension:")
        print(filename + ", must be of type .bmp")
        sys.exit()

def main():
    action_parser = argparse.ArgumentParser(description='stegonography')

    # either encrypt or decrypt
    group = action_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--create", help="create stego image", action='store_true')
    group.add_argument("-e", "--extract", help="extract secret image", action='store_true')

    # parser for option --create
    parser_create = argparse.ArgumentParser()
    parser_create.add_argument("cover_img", metavar="cover_image", help="cover image file") 
    parser_create.add_argument("secret_img", metavar="secret_image", help="secret image file") 
    parser_create.add_argument("output_name", metavar="output_name", help="name of the output file") 
    parser_create.add_argument("password", metavar="password", help="password for encrypt/decrypt secret image") 
    # parser for option --extract
    parser_extract = argparse.ArgumentParser()
    parser_extract.add_argument("stego_img", metavar="stego_image", help="image file to extract")
    parser_extract.add_argument("password", metavar="password", help="password required for decryption")

    # evalute which action to perform - create or extract
    args = action_parser.parse_known_args(sys.argv[1:])
    if args[0].create:
        args = parser_create.parse_args(sys.argv[2:])
        args.password = factor_passwd(args.password)
        check_extension(args.cover_img)
        check_extension(args.secret_img)
        check_extension(args.output_name)
        create_stego_image(args.cover_img, args.secret_img, args.output_name, args.password)
    else:
        args = parser_extract.parse_args(sys.argv[2:])
        args.password = factor_passwd(args.password)
        check_extension(args.stego_img)
        extract_secret_image(args.stego_img, args.password)

# main function
if __name__ == "__main__":
    main()
