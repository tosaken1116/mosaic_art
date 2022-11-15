import json
from pathlib import Path

import extcolors
import numpy as np
from colormap import hex2rgb, rgb2hex
from PIL import Image


def trimm_png():
    p = Path('get_img/')
    src_img_list = list(p.glob('*.png'))
    new_size = 100

    for i, src_img in enumerate(src_img_list):

        img = Image.open(src_img)
        # img = img.convert(mode="L")
        center_x = int(img.width / 2)
        center_y = int(img.height / 2)
        img_size = int(img.height)  if img.width>img.height else int(img.width)
        img_crop = img.crop((center_x - img_size / 2, center_y - img_size / 2, center_x + img_size / 2, center_y + img_size / 2))

        img_resize = img_crop.resize((new_size, new_size))
        img_resize.save('trimmed_img/photo' + str(i) + '.png', 'PNG', quality=100, optimize=True)

def exact_color(resize, tolerance):
    color_dict={}
    p = Path('trimmed_img/')
    trimmed_img_list = list(p.glob('*.png'))
    print(trimmed_img_list)
    for trimmed_img in trimmed_img_list:
        colors_x = extcolors.extract_from_path(trimmed_img, tolerance=tolerance, limit=10)
        colors_pre_list = str(colors_x).replace('([(', '').split(', (')[0:-1]
        df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
        average_color_list = [rgb.replace('(','').replace(")", "").split(', ') for rgb in df_rgb]
        print(average_color_list)
        average_color=[0,0,0]
        print(trimmed_img)
        # if len(average_color_list) == 2:
        for i in range(2):
            for j in range(2):
                print(int(average_color_list[i][j]))
                # print(average_color_list[j])
                average_color[j] +=int(average_color_list[i][j])
        # elif len(average_color_list) == 3:
        #     for i in range(3):
        #         for j in range(3):
        #             print(int(average_color_list[i][j]))
        #             # print(average_color_list[j])
        #             average_color[j] +=int(average_color_list[i][j])
        df_rgb=[int(average_color[0]/3),int(average_color[1]/3),int(average_color[2]/3)]
        df_color_up = rgb2hex(df_rgb[0],df_rgb[1],df_rgb[2])
        color_dict[df_color_up]=str(trimmed_img)
    with open('color_dict.json', 'w') as f:
        json.dump(color_dict, f, indent=2, ensure_ascii=False)

def calculate_color_distance(color_code_a,color_code_b):
    rgb_a = list(hex2rgb(color_code_a))
    rgb_b = list(hex2rgb(color_code_b))
    return (rgb_a[0]-rgb_b[0])**2+(rgb_a[1]-rgb_b[1])**2+(rgb_a[2]-rgb_b[2])**2

def make_pixel_picure(picture_path):
    with open('color_dict.json') as f:
        color_dict = json.load(f)
    img = Image.open(picture_path)
    center_x = int(img.width / 2)
    center_y = int(img.height / 2)
    img_size = int(img.height)  if img.width>img.height else int(img.width)
    img_crop = img.crop((center_x - img_size / 2, center_y - img_size / 2, center_x + img_size / 2, center_y + img_size / 2))
    img_resize = img_crop.resize((150, 150))
    img_resize.save('unmade.png')
    # img = cv2.imread(img_resize)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_array = np.asarray(img_resize)
    row_pictures=[]
    i = 0
    for img_row in img_array:
        picture_exist = False
        for img_element in img_row:
            img_rgb_list = img_element.tolist()
            img_color_code = rgb2hex(img_rgb_list[0],img_rgb_list[1],img_rgb_list[2])
            if img_color_code in color_dict.keys():
                picture_path = color_dict[img_color_code]
            else:
                picture_path = color_dict[get_near_color_code(color_dict.keys(),img_color_code)]
            if not picture_exist:
                row_picture =Image.open(picture_path)
                picture_exist=True
            row_picture = get_concat_h(row_picture,Image.open(picture_path))
            i+=1
            print(i)
        # row_picture.save(f'{i}row_picture.png')
        print(row_picture)
        row_pictures.append(row_picture)
    print(len(row_pictures))
    picture = row_pictures[0]
    for index,row_picture in enumerate(row_pictures):
        if index == 0:
            pass
        else:
            print(index)
            print(row_picture)
            picture = get_concat_v(picture,row_picture)
    picture.save('made_picture.png')
def get_near_color_code(color_keys,compare_code):
    distance = 196608
    return_code = ""
    for color_key in color_keys:
        color_distance = calculate_color_distance(color_key,compare_code)
        if color_distance < distance:
            return_code = color_key
            distance= color_distance
    return return_code
def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst
def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst
trimm_png()
exact_color(100,36)
make_pixel_picure('./test.png')
