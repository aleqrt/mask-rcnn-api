import os
import json
import glob
import argparse


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
        asset = data['assets']
        for img in asset:
            name = asset[img]['asset']['name']
            name = name[:-4] + '.json'
            with open(os.path.join(output_folder, name), 'w') as outfile:
                json.dump(asset[img], outfile, indent=4)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Convert annotations from VoTT JSON to json file for each image')
    argparser.add_argument('-o', '--output', help='destination folder for the converted json VOC annotations')
    argparser.add_argument('-i', '--input', help='path to the collection of JSON VOC annotations')

    args = argparser.parse_args()

    main(args.input, args.output)
