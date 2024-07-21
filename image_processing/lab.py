#!/usr/bin/env python3

"""
6.101 Lab 1: Sam Vinu-Srivatsan
Image Processing
"""

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!
# Note to self: call $ python3 -m pylint lab.py

def get_pixel(image, row, col,edge_effect=None):
    # row-major format:[row0col0,row0col1,row0col2...,row1col0...]
    # rows = 4, cols = 3
    # row3col0 is located at the index: 3*3 (row#*totalcol)+col
    # if pixel is out of bounds
    if row < 0 or col < 0 or row >= image["height"] or col >= image["width"]:
        if edge_effect == "zero":
            return 0
        elif edge_effect == "wrap":
            row %= image["height"]
            col %= image["width"]
        elif edge_effect == "extend":
            col = max(col,0)
            col = min(col,image["width"]-1)
            row = max(row,0)
            row = min(row,image["height"]-1)
    return image["pixels"][row*image["width"]+col]

def set_pixel(image, row, col, color):
    image["pixels"][row*image["width"] + col] = color


def apply_per_pixel(image, func):
    """
    Get each pixel and modify the resulting color with the input function.
    Return a new image.
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [],
    }
    result["pixels"] = [0]*(result["height"]*result["width"])
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda color: 255-color)


# HELPER FUNCTIONS

def kernel_pix(image,pixel,kernel,boundary_behavior):
    """
    pixel: a row, col tuple to index inside image["pixels"]
    kernel: a row-major formatted list of floats (always square, odd # of elements)
    """
    kernel_height = int((len(kernel))**0.5)
    # square: kernel_width = kernel_height
    # how much of the pixel to extend in each direction to apply kernel
    pix_extend = int(kernel_height//2)
    # starting pixel coordinates within image["pixels"] around center pixel
    pix_row = pixel[0]-pix_extend
    pix_col = pixel[1]-pix_extend
    # loop through image indices
    color = 0  # final color of pixel after applying kernel
    col_boundary = pix_col+kernel_height-1
    for k in kernel:
        color += get_pixel(image,pix_row,pix_col,boundary_behavior) * k
        if pix_col == col_boundary:
            pix_row+=1
            pix_col = pixel[1]-pix_extend
        else:
            pix_col+=1
    return color


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    To most easily match indices surrounding each pixel in an image,
    we can format the kernel in row-major formatted list like the image pixels.
    """
    # loop through pixels list and call kernel pix on each of them
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": []
        }
    for pix_index in range(len(image["pixels"])):
        # extract the row and column from the index
        p_col = pix_index%image["width"] # remainder
        p_row = (pix_index - p_col)//image["width"]
        result["pixels"].append(kernel_pix(image,(p_row,p_col),kernel,boundary_behavior))
    return result


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for index in range(len(image["pixels"])):
        if image["pixels"][index] > 255:
            image["pixels"][index] = 255
        elif image["pixels"][index] < 0:
            image["pixels"][index] = 0
        else:
            image["pixels"][index] = round(image["pixels"][index])
    return image

# FILTERS
def create_box_kernel(n):
    return [1/n**2]*n**2

def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = create_box_kernel(kernel_size)
    # then compute the correlation of the input image with that kernel
    blurred_image = correlate(image,kernel,"extend")
    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(blurred_image)

def sharpened(image,n):
    """
    Return a new image representing the result of subtracting an "unsharp" (blurred)
    version of the image from the original image scaled by 2.

    This process does not mutate the input image; it creates a new sharp_img
    variable in the same dictionary format as the input parameter image.
    """
    kernel = create_box_kernel(n)
    blur_img = correlate(image,kernel,"extend")
    sharp_img = {"height":image["height"],
                 "width": image["width"],
                 "pixels":[]
                 }
    for i,color in enumerate(image["pixels"]):
        sharp_img["pixels"].append(2*color - blur_img["pixels"][i])
    return round_and_clip_image(sharp_img)

def edges(image):
    """
    Return a new image representing the result after applying the Sobel operator
    filter to the original image.

    This is done by correlating the image with
    two kernels (k1 and k2) to create two output images (o1 and o2), taking
    the rounded square root of the square of the output sums of every pixel.
    """
    k1 = [-1,-2,-1,0,0,0,1,2,1]
    k2 = [-1,0,1,-2,0,2,-1,0,1]
    o1 = correlate(image,k1,"extend")
    o2 = correlate(image,k2,"extend")
    output_img = {"height":image["height"],
                 "width": image["width"],
                 "pixels":[]
                 }
    for o1_pixel, o2_pixel in zip(o1["pixels"],o2["pixels"]):
        output_pixel = round(math.sqrt(o1_pixel**2+o2_pixel**2))
        output_img["pixels"].append(output_pixel)
    return round_and_clip_image(output_img)


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    # ## SECTION 3 IMAGE GENERATION
    # bluegill = load_greyscale_image("test_images/bluegill.png")
    # save_greyscale_image(inverted(bluegill),"inverted_bluegill.png")

    # ## SECTION 4 IMAGE GENERATION
    # pigbird = load_greyscale_image("test_images/pigbird.png")
    # kernpig = [0]*13**2
    # kernpig[26] = 1
    # save_greyscale_image(correlate(pigbird,kernpig,"zero"),"zero_kernel_pigbird.png")
    # save_greyscale_image(correlate(pigbird,kernpig,"extend"),"extend_kernel_pigbird.png")
    # save_greyscale_image(correlate(pigbird,kernpig,"wrap"),"wrap_kernel_pigbird.png")

    # ## SECTION 5 CENTERED PIXEL TESTING
    # load centered_pixel.png to get dimensions for test case
    # centered = load_greyscale_image("test_images/centered_pixel.png")
    # print("centered_pixel height is: ",centered["height"])
    # print("centered_pixel width is: ",centered["width"])
    # print("centered_pixel pixels is: ",centered["pixels"])

    # ## SECTION 5.1 IMAGE GENERATION
    # cat = load_greyscale_image("test_images/cat.png")
    # save_greyscale_image(blurred(cat,13),"blurred_cat.png")

    # ## SECTION 5.2 IMAGE GENERATION
    # pyth = load_greyscale_image("test_images/python.png")
    # save_greyscale_image(sharpened(pyth,11),"sharpened_python.png")

    ## SECTION 6.1 IMAGE GENERATION
    construct = load_greyscale_image("test_images/construct.png")
    save_greyscale_image(edges(construct),"edge_construct.png")
