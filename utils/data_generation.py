"""
Il seguente script permette la realizzazione di un dataset sintetico.

 Il dataset contenete le immagini di background e la cartella con le immagini dei componenti deve trovarsi al path
   - .../[PATH]/data_augmentation/

 Il dataset contenete le immagini con i ritagli dei singoli componenti deve trovarsi nella sottocartella
   - .../[PATH]/data_augmentation/images/

 Le annotazioni dei singoli componenti si trovano nella sottocartella
   - .../[PATH]/data_augmentation/annots/vott-json-export/json_singoli_componenti
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


def decision(probability):
    return random.random() < probability


def is_possible(pixel_occupated, x1, y1, w1, h1):
    for i in range(len(pixel_occupated)):
        x2, y2, w2, h2 = pixel_occupated[i, :]
        # Calculate intersection
        comp_ind = Rectangle(Point(x1, y1 + h1), Point(x1 + w1, y1))
        comp_i = Rectangle(Point(x2, y2 + h2), Point(x2 + w2, y2))
        if comp_ind.intersects(comp_i):
            return False
    return True


def random_position(W, H, w, h):
    x = np.random.randint(1, W - w)
    y = np.random.randint(1, H - h)
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
    new_annot['asset'] = {"format": "JPG",
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
        - images_path:  path in which are images in .PNG or .JPG

        - annots_path: path in which are annotation in .JSON
    """
    annots = [f for f in os.listdir(annots_path) if os.path.isfile(os.path.join(annots_path, f))]

    components_path = os.path.join(images_path, 'images')
    backgrounds = [os.path.join(images_path, f) for f in os.listdir(images_path) if
                   os.path.isfile(os.path.join(images_path, f))]
    components = [f for f in os.listdir(components_path) if os.path.isfile(os.path.join(components_path, f))]

    tot = 0
    max_count = 2000

    for background in backgrounds:
        background = Image.open(background)
        count = 0

        while count < max_count:
            # creo una copia dello sfondo su cui aggiungere le componenti random
            background_copy = background.copy()
            W, H = background_copy.size

            # utilizzo un array di supporto per verificare che la posizione nell'img sia disponibile per aggiungere un componente
            pixel_occupated = np.zeros([len(components), 4], dtype=int)

            new_annot = dict()
            new_annot['regions'] = list()
            ind = 0

            # selezione random in modo da evitare bias verso i primi componenti della lista
            num_comp = 20
            comps = random.sample(components, num_comp)

            for component in comps:
                comp = Image.open(os.path.join(components_path, component))

                # Decommentare la riga seguente per avere le immagini BLUR dei singoli componenti
                if tot > max_count/2:
                    comp = comp.filter(ImageFilter.GaussianBlur)

                w, h = comp.size

                # Ciclo (per un massimo di 1000 volte) per l'inserimento di un componente senza overlap con gli altri
                for i in range(1000):
                    x, y = random_position(W, H, w, h)

                    # verifico se è possibile aggiungere un nuovo componente NON sovrapposto
                    if is_possible(pixel_occupated, x, y, w, h):
                        pixel_occupated[ind, :] = x, y, w, h
                        background_copy.paste(comp, (x, y), comp)

                        # se aggiungo img di cavi per creare rumore non li considero nel file di annotazioni
                        if 'cavi' not in component[:-4]:
                            annot_name = os.path.join(annots_path, annots[annots.index(component[:-4]+'.json')])
                            file = open(annot_name, encoding='utf-8')
                            annot = json.load(file)
                            file.close()

                            for j, reg in enumerate(annot['regions']):
                                new_annot['regions'].append(new_annotation(annot['regions'][j], x, y))

                        ind += 1
                        break

            # split train e test set
            if decision(0.3):
                destination_dir_images = 'dataset/elettrocablaggi_20200921/0A00018253.04/test/images/'
                destination_dir_annots = 'dataset/elettrocablaggi_20200921/0A00018253.04/test/annots/'
            else:
                destination_dir_images = 'dataset/elettrocablaggi_20200921/0A00018253.04/train/images/'
                destination_dir_annots = 'dataset/elettrocablaggi_20200921/0A00018253.04/train/annots/'

            new_file_name = 'synthetic_image_%s' % tot
            tot += 1
            count += 1

            print(destination_dir_images + new_file_name + '.jpg')

            background_copy.save(destination_dir_images + new_file_name + '.jpg')
            save_annot(new_annot, new_file_name, destination_dir_images, destination_dir_annots, background_copy)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Data augmentation script')
    argparser.add_argument('-a', '--annots', help='folder path of json VOC annotations of single component')
    argparser.add_argument('-i', '--images', help='folder path in which are images, annots and backgrounds')

    args = argparser.parse_args()

    main(args.images, args.annots)
