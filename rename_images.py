from PIL import Image
import os, glob


def resize_files():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = dir_path + '/staticfiles/images/CardImages/'
    # input(path)
    # input(path2)

    for filename in glob.glob(path+'*.jpg'):
        base_name = os.path.basename(filename)
        name, ext = os.path.splitext(base_name)
        if " " in name:
            new_name = name.replace(" ", "_")
            new_name = new_name + ".jpg"
            new_file_name = path + new_name
            print("rename", filename, "to", new_file_name)
            os.rename(filename, new_file_name)

    for filename in glob.glob(path+'*.png'):
        base_name = os.path.basename(filename)
        name, ext = os.path.splitext(base_name)
        new_name = name.replace(" ", "_")
        new_name = new_name + ".jpg"
        new_file_name = path + new_name
        print("rename", filename, "to", new_file_name)
        os.rename(filename, new_file_name)

    for filename in glob.glob(path+'*.webp'):
        base_name = os.path.basename(filename)
        name, ext = os.path.splitext(base_name)
        new_name = name.replace(" ", "_")
        new_name = new_name + ".jpg"
        new_file_name = path + new_name
        print("rename", filename, "to", new_file_name)
        os.rename(filename, new_file_name)


def make_jpg():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = dir_path + '/staticfiles/images/CardImages/'
    # input(path)
    # input(path2)
    for filename in glob.glob(path):
        base_name = os.path.basename(filename)
        current_image, ext = os.path.splitext(base_name)
        card_name = current_image.replace("_", " ")
        if ext == "png" or ext == "jpg":
            with Image.open(path + filename) as im:
                im = im.convert("RGB")
                im.save(path + filename)


make_jpg()
resize_files()
