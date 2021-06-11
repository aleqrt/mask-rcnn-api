import argparse
import json
import os
import string
from random import random

import cv2
import numpy as np


def save(new_file_name, old_annot, images_path, annots_path):
    new_annot = dict()
    new_annot['regions'] = list()

    width = old_annot['asset']['size']['width']
    height = old_annot['asset']['size']['height']
    for region in old_annot['regions']:
        new_annot['regions'].append(region)

    new_annot['asset'] = {"format": "png",
                          "id": ''.join(
                              random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                          "name": new_file_name[:-5] + '.jpg',
                          "path": images_path + new_file_name[:-5] + '.jpg',
                          "size": {
                              "width": width,
                              "height": height
                          },
                          "state": 2,
                          "type": 1
                          }
    with open(os.path.join(annots_path, new_file_name), 'w') as outfile:
        json.dump(new_annot, outfile, indent=4)


def getHomography(kpsA, kpsB, matches, reprojThresh):
    # convert the keypoints to numpy arrays
    kpsA = np.float32([kp.pt for kp in kpsA])
    kpsB = np.float32([kp.pt for kp in kpsB])

    if len(matches) > MIN_MATCH_COUNT:

        # construct the two sets of points
        ptsA = np.float32([kpsA[m.queryIdx] for m in matches])
        ptsB = np.float32([kpsB[m.trainIdx] for m in matches])

        # estimate the homography between the sets of points
        H, _ = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, reprojThresh)

        return H
    else:
        raise RuntimeError('Can’t find enough keypoints.')


def main(imgs_dir, annotation_dir, warp_images):
    SIFT = cv2.xfeatures2d.SIFT_create()

    global MIN_MATCH_COUNT
    MIN_MATCH_COUNT = 5

    info = {
        'annotation_dir': annotation_dir,
        'images_dir': imgs_dir,
        'warp_dir': warp_images
    }

    images = [f for f in os.listdir(info['images_dir']) if os.path.isfile(os.path.join(info['images_dir'], f))]

    f = open(info['annotation_dir'] + images[0][:-4] + '.json', encoding='utf-8')
    annotation = json.load(f)
    f.close()

    image_left = cv2.cvtColor(cv2.imread(info['images_dir'] + images[0]), cv2.COLOR_BGR2RGB)
    image_left_gray = cv2.cvtColor(image_left, cv2.COLOR_RGB2GRAY)
    kp_left, descriptors_left = SIFT.detectAndCompute(image_left_gray, None)

    # len(kp_left)

    try:
        images.remove(image_left)
    except:
        print("No element")

    for img in images:
        image_right = cv2.cvtColor(cv2.imread(info['images_dir'] + img), cv2.COLOR_BGR2RGB)
        image_right_gray = cv2.cvtColor(image_right, cv2.COLOR_RGB2GRAY)

        kp_right, descriptors_right = SIFT.detectAndCompute(image_right_gray, None)

        # len(kp_right)

        ratio = .8

        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

        matches = bf.knnMatch(descriptors_right, descriptors_left, k=2)

        good = []

        for m, n in matches:
            # ensure the distance is within a certain ratio of each
            # other (i.e. Lowe's ratio test)
            if m.distance < n.distance * ratio:
                good.append(m)
        matches = np.asarray(good)

        # matches.shape

        H = getHomography(kp_right, kp_left,
                          matches, 5)

        img_right_warp = cv2.warpPerspective(image_right, H, (image_right.shape[1], image_right.shape[0]))

        new_name = info['warp_dir'] + img[:-4] + '_warp.jpg'
        cv2.imwrite(new_name, img_right_warp)

        new_name_json = info['annotation_dir'] + img[:-4] + '_warp.json'
        save(new_name_json, annotation, info['images_dir'], info['annotation_dir'])
        print(new_name + " OK!")


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Data augmentation script')
    argparser.add_argument('-a', '--annots', help='folder path of json')
    argparser.add_argument('-i', '--images', help='folder path of images')
    argparser.add_argument('-w', '--warp_images', help='folder path of warp images')

    args = argparser.parse_args()

    main(args.images, args.annots, args.warp_images)
