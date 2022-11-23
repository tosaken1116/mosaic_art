import datetime
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import cv2
import extcolors
import numpy as np
import tqdm
from apiclient.discovery import build
from colormap import hex2rgb, rgb2hex
from colormath.color_conversions import convert_color as cm_convert_color
from colormath.color_diff import delta_e_cie2000 as cm_delta_e_cie2000
from colormath.color_objects import LabColor as cm_LabColor
from colormath.color_objects import sRGBColor as cm_sRGBColor
from dotenv import load_dotenv
from PIL import Image

# load_dotenv()
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./youtubeapi.json"
# DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')

# YOUTUBE_API_SERVICE_NAME = 'youtube'
# YOUTUBE_API_SERVICE_VERSION = 'v3'

# youtube = build(
#     YOUTUBE_API_SERVICE_NAME,
#     YOUTUBE_API_SERVICE_VERSION,
#     developerKey=DEVELOPER_KEY
# )
Image.MAX_IMAGE_PIXELS = 1000000000
XYZ_MATRIX = np.array([
            [0.4124, 0.2126, 0.0193],
            [0.3576, 0.7152, 0.1192],
            [0.1805, 0.0722, 0.9505]
            ])
class MisaicArt:
    image_resolution = 50
    # def trimme_youtube_thumnail_image():

    def download_image(detect_word):
        download_urls =GetYouTube.get_song_dict_of_channel_by_detect_word(detect_word)
        for download_url in tqdm.tqdm(download_urls,desc=f"{'    download_image': <25}",leave=False):
            MisaicArt.download_file(download_url)
    def trimm_png():
        p = Path('get_img/')
        src_img_list = list(p.glob('*.png'))
        new_size = MisaicArt.image_resolution

        for i, src_img in enumerate(tqdm.tqdm(src_img_list,desc=f"{'    trim_image': <25}",leave=False)):
            img = Image.open(src_img)
            try:
                dte = datetime.datetime.strptime(str(src_img).replace('get_img/',"").replace('.png',""), '%Y-%m-%d %H:%M:%S.%f')
                img = img.crop((center_x - img_size / 2, center_y - img_size / 2, center_x + img_size / 2, center_y + img_size / 2))
            # if str(src_img).replace('get_img/',"").replace('.png/',"")
            # img = img.convert(mode="L")
            except:
                pass
            center_x = int(img.width / 2)
            center_y = int(img.height / 2)
            img_size = int(img.height)  if img.width>img.height else int(img.width)
            img_crop = img.crop((center_x - img_size / 2, center_y - img_size / 2, center_x + img_size / 2, center_y + img_size / 2))

            img_resize = img_crop.resize((new_size, new_size))
            img_resize.save('trimmed_img/photo' + str(i) + '.png', 'PNG', quality=100, optimize=True)
            img_resize = img_crop.resize((1, 1))
            img_resize.save('color_code_img/photo' + str(i) + '.png', 'PNG', quality=100, optimize=True)

    def exact_color(tolerance):
        color_dict={}
        p = Path('color_code_img/')
        trimmed_img_list = list(p.glob('*.png'))
        for trimmed_img in tqdm.tqdm(trimmed_img_list,desc= f"{'     generate_color_dict': <25}",colour="#ff4444",leave=False):
            colors_x = extcolors.extract_from_path(trimmed_img, tolerance=tolerance, limit=10)
            colors_pre_list = str(colors_x).replace('([(', '').split(', (')[0:-1] #距離込みRGB
            df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list] #RGB
            average_color_list = [rgb.replace('(','').replace(")", "").split(', ') for rgb in df_rgb] #RGB_list
            # print(type(average_color_list[0]))
            # if int(colors_pre_list[0].split(',')[3].replace(')',''))>color_hardle[0]:
            average_color_list=str(colors_x).replace('([((', '').replace(' ', '').split(')')[0].split(',')
            df_rgb=[int(average_color_list[0]),int(average_color_list[1]),int(average_color_list[2])]
            df_color_up = rgb2hex(df_rgb[0],df_rgb[1],df_rgb[2])
            if color_dict.get(df_color_up) is None:
                color_dict[df_color_up]=str(trimmed_img).replace('color_code_img','trimmed_img')
                color_dict[df_color_up]=str(trimmed_img).replace('color_code_img','trimmed_img')
        with open('color_dict.json', 'w') as f:
            json.dump(color_dict, f, indent=2, ensure_ascii=False)


    def make_pixel_picure(picture_path,resize,crop_bool):
        with open('color_dict.json') as f:
            color_dict = json.load(f)
        img = Image.open(picture_path)
        if crop_bool:
            center_x = int(img.width / 2)
            center_y = int(img.height / 2)
            img_size = int(img.height)  if img.width>img.height else int(img.width)
            img_crop = img.crop((center_x - img_size / 2, center_y - img_size / 2, center_x + img_size / 2, center_y + img_size / 2))
            img_resize = img_crop.resize((resize, resize))
        else:
            img_resize = img.resize((int(resize*img.width /img.height), resize)) if img.width>img.height else   img.resize((resize, int(resize*img.height/img.width)))
        img_resize.save('unmade.png')
        img_array = np.asarray(img_resize)
        row_pictures=[]
        for index,img_row in enumerate(tqdm.tqdm(img_array,desc= f"{'     make_row_image': <25}",colour= "#00ffff",leave=False)):
            picture_exist = False
            for img_element in img_row:
                img_rgb_list = img_element.tolist()
                img_color_code = rgb2hex(img_rgb_list[0],img_rgb_list[1],img_rgb_list[2])
                if img_color_code in color_dict.keys():
                    picture_path = color_dict[img_color_code]
                else:

                    picture_path = color_dict.get(MisaicArt.get_near_color_code(color_dict.keys(),img_color_code))
                if not picture_exist:
                    if picture_path is not None:
                        row_picture =Image.open(picture_path)
                    else:
                        row_picture = Image.new('RGB',(MisaicArt.image_resolution,MisaicArt.image_resolution),(255,0,0))
                        # row_picture = Image.new('RGB',(MisaicArt.image_resolution,MisaicArt.image_resolution),(img_rgb_list[0],img_rgb_list[1],img_rgb_list[2]))
                    picture_exist=True
                if picture_path is not None:
                    add_picture =Image.open(picture_path)
                else:
                    add_picture = Image.new('RGB',(MisaicArt.image_resolution,MisaicArt.image_resolution),(255,0,0))
                    # add_picture = Image.new('RGB',(MisaicArt.image_resolution,MisaicArt.image_resolution),(img_rgb_list[0],img_rgb_list[1],img_rgb_list[2]))
                row_picture = MisaicArt.get_concat_h(row_picture,add_picture)
            row_pictures.append(row_picture)
        picture = row_pictures[0]
        for index,row_picture in enumerate(tqdm.tqdm(row_pictures,desc= f"{'     connect_image': <25}",leave=False)):
            if index == 0:
                pass
            else:
                picture = MisaicArt.get_concat_v(picture,row_picture)
        now = datetime.datetime.now()
        picture.save(f"./made_img/{now}.png")

    def get_near_color_code(color_keys,compare_code):
        distance = 196608
        return_code = ""
        for color_key in color_keys:
            color_distance = MisaicArt.calculate_color_distance(color_key,compare_code)
            if color_distance < distance:
                return_code = color_key
                distance= color_distance
        return return_code
        # return return_code if distance <5000 else None

    def calculate_color_distance(color_a,color_b):
        if type(color_a) != list:
            color_a = list(hex2rgb(color_a))
            color_b = list(hex2rgb(color_b))
        # RGB1 = np.array(color_a,np.uint8)
        # RGB2 = np.array(color_b,np.uint8)

        # return cm_delta_e_cie2000(MisaicArt.colormath_rgb2lab(RGB1), MisaicArt.colormath_rgb2lab(RGB2))
        return (int(color_a[0])-int(color_b[0]))**2+(int(color_a[1])-int(color_b[1]))**2+(int(color_a[2])-int(color_b[2]))**2

    def colormath_rgb2lab(rgb):
        return cm_convert_color(cm_sRGBColor(*(rgb / 255)), cm_LabColor, target_illuminant='d65')

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

    def download_file(url):
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            now = datetime.datetime.now()
            with open(f"./download_img/{str(now)}.png", mode='wb') as local_file:
                local_file.write(data)

    def compare_image(picture_path,crop_bool,resize):
        img = Image.open(picture_path)
        if crop_bool:
            center_x = int(img.width / 2)
            center_y = int(img.height / 2)
            img_size = int(img.height)  if img.width>img.height else int(img.width)
            img_crop = img.crop((center_x - img_size / 2, center_y - img_size / 2, center_x + img_size / 2, center_y + img_size / 2))
            img_resize = img_crop.resize((resize, resize))
        else:
            # print((int(resize*img.height /img.width)))
            img_resize = img.resize((int(resize*img.width /img.height), resize)) if img.width>img.height else   img.resize((resize, int(resize*img.height/img.width)))
        img_resize.save('compare.png')
        img_array = np.asarray(img_resize)
        raw_image = Image.open("./unmade.png")
        raw_img_array = np.asarray(raw_image)
        color_accuracy=0.0
        for row_index,img_row in enumerate(tqdm.tqdm(img_array,desc= f"{'     compare': <25}",leave=False)):
            for col_index, img_element in enumerate(img_row):
                img_rgb_list = img_element.tolist()
                compare_img_rgb_list = raw_img_array[row_index][col_index].tolist()
                color_accuracy += 1 if MisaicArt.calculate_color_distance(img_rgb_list,compare_img_rgb_list)<10 else 0
                # color_accuracy += (196608.0 - MisaicArt.calculate_color_distance(img_rgb_list,compare_img_rgb_list))/196608
        print(f"{int(color_accuracy/(resize*resize)*100)}%")
def shape_movie_image():
    p = Path('cut_image/')
    src_img_list = list(p.glob('*.png'))
    for i,src_img in enumerate(src_img_list):
        img = Image.open(src_img)
        rotate_img =img.rotate(180)
        crop_img = rotate_img.crop((320-265,0,320+265,296))
        crop_img.save(src_img)
def save_all_frames(video_path, dir_path, basename, ext='png'):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)

    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    n = 0

    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(f'{base_path}_{str(n).zfill(digit)}.{ext}', frame)
            n += 1
        else:
            return
def convert_img_to_movie():
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter('video.mp4',fourcc, 20.0, ( 10000,17947))
    directory = os.listdir("./made_img")
    files = [f for f in directory if os.path.isfile(os.path.join("./made_img", f))]
    for file in files :
        # hoge0000.png, hoge0001.png,..., hoge0090.png
        if ".png" in file:
            img = cv2.imread(file)

            # can't read image, escape
            if img is None:
                print("can't read")
                break

            # add
            video.write(img)

    video.release()
    print('written')
# save_all_frames("./seed_movie/test.mp4","./cut_image","test")
# shape_movie_image()
class GetYouTube:
    @classmethod
    def get_song_dict_of_channel_by_detect_word(cls,detect_word:str):
        search_response = youtube.search().list(
            part = 'id,snippet',
            q=detect_word,
            maxResults=1,
            order='relevance',
            type='channel'
        ).execute()
        song_dicts_array = cls.get_song_dicts_array_of_channel(search_response['items'][0]['id']['channelId'])
        return song_dicts_array
    def get_song_dicts_array_of_channel(channel_id:str):
        nextpagetoken = None
        song_dicts_array_of_vocaloP = []
        get_category_string_list =["初音ミク","IA","鏡音リン","鏡音レン","可不","GUMI","flower"]
        while True:
            if nextpagetoken != None:
                nextpagetoken = nextPagetoken
            try:
                channel_response = youtube.search().list(
                    part = 'id,snippet',
                    order = "viewCount",
                    maxResults=80,
                    channelId = channel_id,
                    pageToken = nextpagetoken,
                    type='video',
                ).execute()
                for search_result in channel_response.get('items',[]):
                    for category_string in get_category_string_list:
                        if category_string in str(search_result['snippet']['title']):
                            song_dicts_array_of_vocaloP.append(f"https://img.youtube.com/vi/{search_result['id']['videoId']}/mqdefault.jpg")
            except:
                break
            try:
                nextPagetoken = channel_response['nextPageToken']
            except:
                break
        return song_dicts_array_of_vocaloP
# MisaicArt.download_image('ピノキオピー')
# MisaicArt.trimm_png()

# MisaicArt.exact_color(36)
# p = Path('cut_image/')
# src_img_list = list(p.glob('*.png'))
# for src_img in tqdm.tqdm(src_img_list,position=0,desc= f"{'generate_pixel_image': <25}"):
#     MisaicArt.make_pixel_picure(src_img,50,False)
convert_img_to_movie()