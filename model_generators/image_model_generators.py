import sys, json
import numpy as np
from ds_utils import add_output_model
import ds_utils
import os.path


#TODO DELETE
def generate_image_model(image_path):
    filename = os.path.basename(image_path)
    name_ = "image_{}".format(filename)
    model = {
        "type": "string",
        "name": name_,
        "string": image_path,
    }
    return model


if __name__ == '__main__':
    pass
