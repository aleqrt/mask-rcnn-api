import argparse
import cv2 as cv2
import os
import json
import string
import random
import warnings
import numpy as np
from scipy import ndarray
import skimage as sk
from skimage import transform
from skimage import filters
from skimage import io
from skimage.util import random_noise
from skimage.util import invert

with warnings.catch_warnings():
    warnings.simplefilter("ignore")


def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def new_xy_coord(region, w, h, key, random_degree):
    """
    NOTA:
        -   res['boundingBox']['left'], contiente la coordinata X del punto in alto a sinistra del bbox
        -   res['boundingBox']['top'], contiente la coordinata Y del punto in alto a sinistra del bbox
    """
    res = {'id': region['id'], 'type': region['type'], 'tags': region['tags'], 'boundingBox': dict(), 'points': list()}
    width = region['boundingBox']['width']
    height = region['boundingBox']['height']

    if key == 'horizontal_flip':
        res['boundingBox']['height'] = height
        res['boundingBox']['width'] = width

        res['boundingBox']['left'] = 2 * (w / 2 - region['boundingBox']['left']) + region['boundingBox']['left']
        res['boundingBox']['top'] = region['boundingBox']['top']

        for point in region['points']:
            res['points'].append({'x': 2 * (w / 2 - point['x']) + point['x'], 'y': point['y']})

        return res

    elif key == 'rotate90' or key == 'rotate270':
        res['boundingBox']['height'] = width
        res['boundingBox']['width'] = height

        theta = np.radians(random_degree)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array([[c, -s], [s, c]]).transpose()
        xy = np.array([region['boundingBox']['left'], region['boundingBox']['top']])
        vett = np.abs(np.dot(xy, R))

        if random_degree == 90:
            vett = vett + np.array([0, 2 * (h / 2 - vett[1])])
        elif random_degree == 270:
            vett = vett + np.array([2 * (w / 2 - vett[0]), 0])

        res['boundingBox']['left'] = vett[0]
        res['boundingBox']['top'] = vett[1]

        for point in region['points']:
            xy = np.array([point['x'], point['y']])
            vett = np.abs(np.dot(xy, R))

            if random_degree == 90:
                vett = vett + np.array([0, 2 * (h / 2 - vett[1])])
            elif random_degree == 270:
                vett = vett + np.array([2 * (w / 2 - vett[0]), 0])

            res['points'].append({'x': vett[0], 'y': vett[1]})
        return res

    else:
        res['boundingBox'] = region['boundingBox']
        res['points'] = region['points']
        return res


def rotation90(image_array: ndarray):
    degree = 90
    return sk.transform.rotate(image_array, degree, resize=True), degree


def rotation270(image_array: ndarray):
    degree = 270
    return sk.transform.rotate(image_array, degree, resize=True), degree


def gaussian_blur(image_array: ndarray):
    return sk.filters.gaussian(image_array, multichannel=True)


def horizontal_flip(image_array):
    return np.fliplr(image_array)


def add_noise(image_array: ndarray):
    return random_noise(image_array)


def invert_image(image_array: ndarray):
    return invert(image_array)


def gamma_correction(image_array, gamma):
    return adjust_gamma(image_array, gamma=gamma)


def save_annot(new_annot, new_file_name, images_path, annots_path, width, height):
    new_annot['asset'] = {"format": "JPG",
                          "id": ''.join(
                              random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                          "name": new_file_name + '.jpg',
                          "path": images_path + new_file_name + '.jpg',
                          "size": {
                              "width": width,
                              "height": height
                          },
                          "state": 2,
                          "type": 1
                          }
    with open(os.path.join(annots_path, new_file_name + '.json'), 'w') as outfile:
        json.dump(new_annot, outfile, indent=4)


def classic_augmentation(images_path, annots_path):
    """
    Main function for data augmentation.
    Params:
        - images_path: path in which are images
        - annots_path: path in which are annotation in json format

    Returns:
        - new images in 'images_path' folder
        - new annotation in 'annots_path' folder
    """
    # dictionary of the transformations we defined earlier
    available_transformations = {
        'rotate90': rotation90,
        'rotate270': rotation270,
        'gaussian_blur': gaussian_blur,
        # 'horizontal_flip': horizontal_flip,
        'add_noise': add_noise,
        'invert_image': invert_image,
        'gamma_correction': gamma_correction
    }

    # find all files paths from the folders
    images_name = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
    annots_name = [a for a in os.listdir(annots_path) if os.path.isfile(os.path.join(annots_path, a))]

    tot = 0

    for i, img in enumerate(images_name):

        # if i == 1:
        #     break

        try:
            file = os.path.join(annots_path, annots_name[annots_name.index(img[:-4] + '.json')])
            f = open(file, encoding='utf-8')
            annot = json.load(f)

            # transformation to apply for a single image
            random_degree = 0
            keys = list(available_transformations)
            for key in keys:
                temp_img = cv2.imread(os.path.join(images_path, img))

                new_annot = dict()
                new_annot['regions'] = list()

                if key == 'rotate90' or key == 'rotate270':
                    aug_img, random_degree = available_transformations[key](temp_img)
                    height = annot['asset']['size']['width']
                    width = annot['asset']['size']['height']
                elif key == 'gamma_correction':
                    for gamma in np.arange(0.5, 3.5, 0.5):
                        # ignore when gamma is 1 (there will be no change to the image)
                        if gamma == 1:
                            continue
                        aug_img = available_transformations[key](temp_img, gamma)
                        width = annot['asset']['size']['width']
                        height = annot['asset']['size']['height']

                        # generete new annotation for the transformed image
                        for region in annot['regions']:
                            new_annot['regions'].append(new_xy_coord(region, width, height, key, random_degree))

                        # write image to the disk
                        new_file_name = f'augmented_image_{key}_{gamma}_{tot}'
                        cv2.imwrite(os.path.join(images_path, new_file_name + '.jpg'), aug_img)
                        save_annot(new_annot, new_file_name, images_path, annots_path, width, height)
                        print(new_file_name + " OK!")
                        tot += 1
                else:
                    aug_img = available_transformations[key](temp_img)
                    width = annot['asset']['size']['width']
                    height = annot['asset']['size']['height']

                if key != 'gamma_correction':
                    # generete new annotation for the transformed image
                    for region in annot['regions']:
                        new_annot['regions'].append(new_xy_coord(region, width, height, key, random_degree))

                    new_file_name = f'augmented_image_{key}_{tot}'

                    if key == 'invert_image':
                        # write image to the disk
                        cv2.imwrite(os.path.join(images_path, new_file_name + '.jpg'), (aug_img * 255).astype(np.uint8))
                    else:
                        cv2.imwrite(os.path.join(images_path, new_file_name + '.jpg'), aug_img)

                    save_annot(new_annot, new_file_name, images_path, annots_path, width, height)
                    print(new_file_name + " OK!")
                    tot += 1

        except:
            print(f"An exception occurred at trasformation {key} applied at image {img}")
            continue


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Data augmentation script')
    argparser.add_argument('-a', '--annots', help='folder path of json')
    argparser.add_argument('-i', '--images', help='folder path of images')

    args = argparser.parse_args()

    classic_augmentation(args.images, args.annots)
