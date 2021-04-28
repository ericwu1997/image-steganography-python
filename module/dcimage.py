from PIL import Image

class PixelLoader:
    img = ''
    row_max = 0
    col_max = 0
    row = 0
    col = 0
    count = 0

    def __init__(self, filename):
        _img = Image.open(filename)
        self.img = _img.convert('RGB')
        self.row_max = _img.size[0]
        self.col_max = _img.size[1]
        self.count = self.total = _img.size[0] * _img.size[1]

    def next_pixel_cordinate(self):
        cordinate = (self.row, self.col)
        if self.count > 0:
            self.count -= 1
            self.col += 1
            self.row = (self.row + 1) if self.col >= self.col_max else self.row
            self.col = self.col%self.col_max
            return cordinate
        else:
            return 0

    def get_dimension(self):
        return (self.row_max, self.col_max)

    def to_int_arry(self): 
        index = 0
        arry = []
        for i in range(self.img.size[0]):
            for j in range(self.img.size[1]):
                pixel = self.img.getpixel((i, j))
                arry.append(pixel[0]) # R
                arry.append(pixel[1]) # G
                arry.append(pixel[2]) # B
        return arry

    def get_pixel_at(self, cordinate):
        return self.img.getpixel(cordinate)

    def edit_pixel_at(self, cordinate, new_pixel):
        self.img.putpixel(cordinate, new_pixel)

    def save(self, _filename):
        self.img.save(_filename)

