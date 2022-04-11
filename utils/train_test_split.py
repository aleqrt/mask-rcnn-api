import os
import argparse
import numpy as np
import shutil


def main(input_path, output_path):
    """select 100 random images to use in the training process"""
    annots_path = os.path.join(input_path, 'annots')
    images_path = os.path.join(input_path, 'images')

    images = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]

    m = len(images)//2

    selected = np.random.choice(images, m, replace=False)

    for s in selected:
        shutil.move(os.path.join(annots_path, s[:-4] + '.json'), os.path.join(output_path, 'annots', s[:-4] + '.sjson'))
        shutil.move(os.path.join(images_path, s), os.path.join(output_path, 'images', s))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Train test script')
    argparser.add_argument('-i', '--input', help='input folder in which is stored the data')
    argparser.add_argument('-o', '--output', help='output folder in which store the data to use in training')

    args = argparser.parse_args()

    main(args.input, args.output)
