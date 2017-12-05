import io
import openslide
import numpy as np
from PIL import Image

# def gen_img_tiles(img_or_bytes_or_path, height, width, print_boxes=False):
#    img_matrix=img_to_numpy_array(img_or_bytes_or_path)
#    img=img_matrix_to_pil_image(img_matrix)
#    imgwidth, imgheight = img.size
#    for i in range(0,imgheight,height):
#        for j in range(0,imgwidth,width):
#            box = (j, i, j+width, i+height)
#            if box[2]<=imgwidth and box[3]<=imgheight:
#                if print_boxes:
#            	    print(box)
#                a = img.crop(box)
#                yield a
from computer import Computer
from factory_utils import factorify_as_computer


def generate_tiles_rects(tile_shape, tile_step, img_shape):
    tiles_rects = []
    x = 0
    y = 0
    img_size_x = img_shape[0]
    img_size_y = img_shape[1]
    x_size = tile_shape[0]
    y_size = tile_shape[1]
    x_step = tile_step[0]
    y_step = tile_step[1]
    while y < img_size_y:
        while x < img_size_x:
            w = x_size
            if x + w >= img_size_x:
                w = img_size_x - x
            h = y_size
            if y + h >= img_size_y:
                h = img_size_y - y
            tiles_rects.append((x, y, w, h))
            x += x_step
        x = 0
        y += y_step
    return tiles_rects


def tiles(pilimg, height, width, print_boxes=False):
    #    img_matrix=img_to_numpy_array(img_or_bytes_or_path)
    #    img=img_matrix_to_pil_image(img_matrix)
    imgwidth, imgheight = pilimg.size
    cols = imgwidth // width
    rows = imgheight // height
    n_tiles = cols * rows
    tiles = []
    #   tiles=np.empty((n_tiles, width, height, len(img.getbands())), dtype='uint8')
    for i in range(0, rows):
        for j in range(0, cols):
            box = (j * width, i * height, j * width + width, i * height + height)
            if box[2] <= imgwidth and box[3] <= imgheight:
                if print_boxes:
                    print(box)
                # tiles[i*cols+j]=img.crop(box)
                tiles.append(pilimg.crop(box))
                #    print(n_tiles)
    return tiles


# def img_to_numpy_array(img_or_bytes_or_path):
#    if isinstance(img_or_bytes_or_path, str):
#        img = Image.open(img_or_bytes_or_path)
#    elif isinstance(img_or_bytes_or_path, bytes):
#        img=Image.open(io.BytesIO(img_or_bytes_or_path))
#    elif isinstance(img_or_bytes_or_path, PIL.Image.Image):
#        img=img_or_bytes_or_path
#    img_arr = np.fromstring(img.tobytes(), dtype=np.uint8)
#    img_arr = img_arr.reshape((img.size[1], img.size[0], len(img.getbands())))
#    return img_arr

def pure_pil_alpha_to_color_v2(pilimg, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

    Simpler, faster version than the solutions above.

    Source: http://stackoverflow.com/a/9459208/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    pilimg.load()  # needed for split()
    background = Image.new('RGB', pilimg.size, color)
    background.paste(pilimg, mask=pilimg.split()[3])  # 3 is the alpha channel
    return background


def img_matrix_to_gray_img_matrix(img_matrix):
    pilimg_gray = img_matrix_to_pil_image(img_matrix, grayscale=True)
    img_gray_matrix = pilimage_to_matrix(pilimg_gray)
    return img_gray_matrix


def img_matrix_to_pil_image(img_matrix, grayscale=False):
    img_matrix = img_matrix.squeeze()
    img = Image.fromarray(img_matrix)
    if grayscale:
        img = img.convert('L')
    return img


def path_to_pilimage(path_):
    return Image.open(path_)


def pilimage_to_matrix(pilimage):
    img_matrix = np.fromstring(pilimage.tobytes(), dtype=np.uint8)
    img_matrix = img_matrix.reshape((pilimage.size[1], pilimage.size[0], len(pilimage.getbands())))
    return img_matrix


def path_to_matrix(path_):
    return pilimage_to_matrix(path_to_pilimage(path_))


def pilimg_to_jpeg(pilimg):
    b = io.BytesIO()
    pilimg.save(b, format="jpeg")
    b.seek(0)
    return b.read()


def jpeg_to_pilimg(jpeg_):
    return Image.open(io.BytesIO(jpeg_))


def jpeg_to_matrix(jpeg_):
    return pilimage_to_matrix(jpeg_to_pilimg(jpeg_))


def tiles_rects_computer_factory(computer_func_params):
    tile_shape = computer_func_params["tile_shape"]
    tile_step = computer_func_params["tile_step"]
    downsample = computer_func_params["downsample"]
    image_path = computer_func_params["image_path"]

    # def computer_(image_path):
    def computer_():
        img = openslide.OpenSlide(image_path)
        level = img.get_best_level_for_downsample(downsample)
        img_shape = img.level_dimensions[level]
        tiles_rects = generate_tiles_rects(tile_shape, tile_step, img_shape)
        return tiles_rects

    return Computer(computer_, None)


image_transform_type__computer_factory = {
    "jpeg_to_matrix": factorify_as_computer(jpeg_to_matrix),
    "pilimage_to_matrix": factorify_as_computer(pilimage_to_matrix),
    "tiles_rects": tiles_rects_computer_factory,
    "rgbapilimage_to_rgbpilimage": factorify_as_computer(pure_pil_alpha_to_color_v2)
}
