"""
Il seguente script permette la realizzazione di un dataset sintetico.

 Il dataset contenete le immagini di background e la cartella dei componenti deve trovarsi al path
   - .../[PATH]/data_augmentation/

 Il dataset contenete le immagini con i ritagli dei singoli componenti deve trovarsi nella sottocartella
   - .../[PATH]/data_augmentation/componenti/

 Le annotazioni dei singoli componenti si trovano nella sottocartella
   - .../[PATH]/data_augmentation/componenti_label/vott-json-export/json_singoli_componenti

 Il risultato della data augmentation viene salvato nel seguente path:
   - dataset/elettrocablaggi_20200921/augmentation
"""

import argparse
import json
import os
import string
import random
import numpy as np
from PIL import Image
from PIL import ImageFilter


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, top_left, bottom_right):
        self.bottom_right = bottom_right
        self.top_left = top_left

    def intersects(self, other):
        if self.top_left.x > other.bottom_right.x or other.top_left.x > self.bottom_right.x:
            return False
        if self.top_left.y < other.bottom_right.y or other.top_left.y < self.bottom_right.y:
            return False
        return True


def is_possible(pixel_occupated, x1, y1, w1, h1):
    for i in range(len(pixel_occupated)):
        x2, y2, w2, h2 = pixel_occupated[i, :]
        # Calculate intersection
        comp_ind = Rectangle(Point(x1, y1 + h1), Point(x1 + w1, y1))
        comp_i = Rectangle(Point(x2, y2 + h2), Point(x2 + w2, y2))
        if comp_ind.intersects(comp_i):
            return False
    return True


def random_position(w, h):
    x = np.random.randint(180, 575 - w)
    y = np.random.randint(245, 800 - h)
    return x, y


def new_annotation(regions, x, y):
    regions['boundingBox']['left'] = float(regions['boundingBox']['left']) + x
    regions['boundingBox']['top'] = float(regions['boundingBox']['top']) + y
    points = regions['points']
    for point in points:
        point['x'] = float(point['x']) + x
        point['y'] = float(point['y']) + y
    regions['points'] = points
    return regions


def save_annot(new_annot, new_file_name, destination_dir_images, destination_dir_annots, background_copy):
    new_annot['asset'] = {"format": "png",
                           "id": ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                           "name": new_file_name + '.jpg',
                           "path": destination_dir_images + new_file_name + '.jpg',
                           "size": {
                               "width": background_copy.size[0],
                               "height": background_copy.size[1]
                           },
                           "state": 2,
                           "type": 1
                           }
    with open(destination_dir_annots + new_file_name + '.json', 'w') as outfile:
        json.dump(new_annot, outfile, indent=4)


def main(images_path, annots_path):
    """
    Main function for data augmentation.
    Params:
        - images_path: path in which are images for data augmentation. Must be contain 'componenti' folder in
                        which is stored images for each component.
        - annots_path: path in which are annotation in .json

    Returns:
        - new images in 'dataset/elettrocabalaggi_20200921/augmentation' folder
        - new annotation in 'dataset/elettrocabalaggi_20200921/annotation' folder

        NOTE:
            create data_augmentation folder in images_path and annots_path folders

    """
    annots = [f for f in os.listdir(annots_path) if os.path.isfile(os.path.join(annots_path, f))]

    components_path = os.path.join(images_path, 'componenti')
    backgrounds = [os.path.join(images_path, f) for f in os.listdir(images_path) if
                   os.path.isfile(os.path.join(images_path, f))]
    components = [f for f in os.listdir(components_path) if os.path.isfile(os.path.join(components_path, f))]

    destination_dir_images = 'dataset/elettrocablaggi_20200921/all/images/'
    destination_dir_annots = 'dataset/elettrocablaggi_20200921/all/annots/'

    tot = 0
    max_count = 10000

    for background in backgrounds:
        background = Image.open(background)
        count = 0

        while count < max_count / len(backgrounds):
            background_copy = background.copy()
            pixel_occupated = np.zeros([len(components), 4], dtype=int)
            new_annot = dict()
            new_annot['regions'] = list()
            ind = 0
            for component in components:
                comp = Image.open(os.path.join(components_path, component))

                # Decommentare la riga seguente per avere le immagini BLUR dei singoli componenti
                if tot > max_count/2:
                    comp = comp.filter(ImageFilter.GaussianBlur)

                w, h = comp.size

                # Ciclo (per un massimo di 1000 volte) per l'inserimento di un componente senza overlap con gli altri
                for i in range(1000):
                    x, y = random_position(w, h)
                    if is_possible(pixel_occupated, x, y, w, h):
                        pixel_occupated[ind, :] = x, y, w, h
                        background_copy.paste(comp, (x, y), comp)
                        annot_name = os.path.join(annots_path, annots[components.index(component)])
                        f = open(annot_name, encoding='utf-8')
                        annot = json.load(f)
                        f.close()
                        new_annot['regions'].append(new_annotation(annot['regions'][0], x, y))
                        ind += 1
                        break

            new_file_name = 'augmented_image_%s' % tot
            tot += 1
            count += 1
            background_copy.save(destination_dir_images + new_file_name + '.jpg')
            save_annot(new_annot, new_file_name, destination_dir_images, destination_dir_annots, background_copy)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Data augmentation script')
    argparser.add_argument('-a', '--annots', help='folder path of json VOC annotations of single component')
    argparser.add_argument('-i', '--images', help='folder path of images of backgrounds and components')

    args = argparser.parse_args()

    main(args.images, args.annots)
