import os
import json
import glob
import random
import string
import argparse
import numpy as np


def new_xy_coordinates(region, h):
    """
    NOTA:
        -   res['boundingBox']['left'], contiente la coordinata X del punto in alto a sinistra del bbox
        -   res['boundingBox']['top'], contiente la coordinata Y del punto in alto a sinistra del bbox
        -   height e width sono invertite poichè l'immagine è ruotata di 90° counterclockwise a causa della annotazione VoTT
    """
    res = {'id': region['id'], 'type': region['type'], 'tags': region['tags'], 'boundingBox': dict(), 'points': list()}
    width = region['boundingBox']['width']
    height = region['boundingBox']['height']

    res['boundingBox']['height'] = width
    res['boundingBox']['width'] = height

    x_coordinates = [point["x"] for point in region['points']]
    y_coordinates = [point["y"] for point in region['points']]

    temp = y_coordinates
    y_coordinates = x_coordinates
    x_coordinates = temp

    y_min = min(y_coordinates)
    x_min = min(x_coordinates)

    x_min = 2 * (h / 2 - x_min) + x_min - height

    res['boundingBox']['left'] = x_min
    res['boundingBox']['top'] = y_min

    for ind, x in enumerate(x_coordinates):
        x = 2 * (h / 2 - x) + x
        res['points'].append({'x': x, 'y': y_coordinates[ind]})

    return res


def save_annot(new_annot, new_file_name, images_path, annots_path, width, height):
    new_annot['asset'] = {"format": "png",
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


def main(input_folder, output_folder):
    """
    Find the annotation file in the directory in which are all images annotations and split the annotations
    for each image.
    """
    asset_names = glob.glob("{}*.json".format(input_folder))

    for asset_name in asset_names:
        # read the annotation file
        f = open(asset_name, encoding='utf-8')
        data = json.load(f)
        f.close()

        # parse the content of the annotation file to create bounding boxes
        assets = data['assets']

        for img in assets:
            name = assets[img]['asset']['name']
            name = name[:-4]

            new_annot = dict()
            new_annot['regions'] = list()

            """
            NOTA:
                Nel caso in cui VoTT durante la fase di annotazione ruota le immagini di 90° in senso antiorario
                => commentare
            """
#             width = assets[img]['asset']['size']['width']
#             height = assets[img]['asset']['size']['height']
#             for region in assets[img]['regions']:
#                 new_annot['regions'].append(region)

            """
                => docommentare
            """
            if assets[img]['asset']['size']['height'] < assets[img]['asset']['size']['width']:
                height = assets[img]['asset']['size']['width']
                width = assets[img]['asset']['size']['height']
                for region in assets[img]['regions']:
                    new_annot['regions'].append(new_xy_coordinates(region, width))

            # TODO: parametrizzare la cartella di destinazione nel caso di immagini ruotate da VoTT
            images_path = 'dataset/elettrocablaggi_20200921/GRETA_230V/all/images/'

            save_annot(new_annot, name, images_path, output_folder, width, height)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Convert annotations from VoTT JSON to file JSON for each image')
    argparser.add_argument('-o', '--output', help='destination folder for the converted json VOC annotations')
    argparser.add_argument('-i', '--input', help='path to the collection of JSON VOC annotations')

    args = argparser.parse_args()

    main(args.input, args.output)
