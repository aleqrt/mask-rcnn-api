import argparse
import os
import json
import string
import random
import numpy as np
from scipy import ndarray
import skimage as sk
from skimage import transform
from skimage import filters
from skimage import io
from sklearn.preprocessing import minmax_scale


def new_xy_coordinates(region, w, h, key, random_degree):
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

        res['boundingBox']['left'] = 2 * (w / 2 - region['boundingBox']['left']) + region['boundingBox']['left'] - width
        res['boundingBox']['top'] = region['boundingBox']['top']

        for point in region['points']:
            res['points'].append({'x': 2 * (w / 2 - point['x']) + point['x'] - width, 'y': point['y']})

        return res

    elif key == 'rotate':
        res['boundingBox']['height'] = width
        res['boundingBox']['width'] = height

        theta = np.radians(random_degree)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array([[c, -s], [s, c]]).transpose()
        xy = np.array([region['boundingBox']['left'], region['boundingBox']['top']])
        vett = np.abs(np.dot(xy, R))

        if random_degree == 90:
            vett = vett + np.array([0, 2 * (h / 2 - vett[1]) - width])
        elif random_degree == 270:
            vett = vett + np.array([2 * (w / 2 - vett[0]) - height, 0])

        res['boundingBox']['left'] = vett[0]
        res['boundingBox']['top'] = vett[1]

        for point in region['points']:
            xy = np.array([point['x'], point['y']])
            vett = np.abs(np.dot(xy, R))

            if random_degree == 90:
                vett = vett + np.array([0, 2 * (h / 2 - vett[1]) - width])
            elif random_degree == 270:
                vett = vett + np.array([2 * (w / 2 - vett[0]) - height, 0])

            res['points'].append({'x': vett[0], 'y': vett[1]})
        return res

    else:
        res['boundingBox'] = region['boundingBox']
        res['points'] = region['points']
        return res


def random_rotation(image_array: ndarray):
    random_degree = np.random.choice([90, 270])
    return sk.transform.rotate(image_array, random_degree, resize=True), random_degree


def gaussian_blur(image_array: ndarray):
    return sk.filters.gaussian(image_array, multichannel=True)


def sharpening(image_array: ndarray):
    sobel = sk.filters.sobel(image_array)
    sobel *= 255
    sobel = np.abs(sobel)
    sharped_image = image_array + sobel
    for i in range(3):
        sharped_image[:, :, i] = minmax_scale(sharped_image[:, :, i])
    return sharped_image


def horizontal_flip(image_array: ndarray):
    return image_array[:, ::-1]


def save_annot(new_annot, new_file_name, images_path, annots_path, width, height):
    new_annot['asset'] = {"format": "png",
                           "id": ''.join(
                               random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                           "name": new_file_name,
                           "path": images_path + new_file_name,
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
        'rotate': random_rotation,
        'gaussian_blur': gaussian_blur,
        'sharpening': sharpening,
        'horizontal_flip': horizontal_flip
    }

    # find all files paths from the folders
    images_name = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
    annots_name = [a for a in os.listdir(annots_path) if os.path.isfile(os.path.join(annots_path, a))]

    num_files = len(images_name)
    tot = 0

    for i in range(num_files):
        # chose random image from the folder
        image = images_name[i]
        file = os.path.join(annots_path, annots_name[images_name.index(image)])
        f = open(file, encoding='utf-8')
        annot = json.load(f)

        # read image as an two dimensional array of pixels and read XML annotation
        image_to_transform = sk.io.imread(os.path.join(images_path, image))

        # transformation to apply for a single image
        random_degree = 0
        keys = list(available_transformations)
        for key in keys:
            new_annot = dict()
            new_annot['regions'] = list()

            if key is 'rotate':
                transformed_image, random_degree = available_transformations[key](image_to_transform)
                height = annot['assets']['size']['width']
                width = annot['assets']['size']['height']
            else:
                transformed_image = available_transformations[key](image_to_transform)
                width = annot['assets']['size']['width']
                height = annot['assets']['size']['height']

            # generete new annotation for the transformed image
            for region in annot['regions']:
                new_annot['regions'].append(new_xy_coordinates(region, width, height, key, random_degree))

            # write image to the disk
            new_file_name = 'classic_augmented_image_%s' % tot
            io.imsave(os.path.join(images_path, new_file_name + '.jpg'), transformed_image)

            save_annot(new_annot, new_file_name, images_path, annots_path, width, height)

            # Incremento contatore per il numero di immagini soggette a trasformazioni
            tot += 1


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Data augmentation script')
    argparser.add_argument('-a', '--annots', help='folder path of json VOC annotations of single component')
    argparser.add_argument('-i', '--images', help='folder path of images of background in which is the component folder'
                                                  ' to create new random data set')

    args = argparser.parse_args()

    classic_augmentation(args.images, args.annots)
