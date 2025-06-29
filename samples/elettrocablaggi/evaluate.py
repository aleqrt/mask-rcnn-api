import os
import sys
import warnings
import numpy as np
import elettrocablaggi
import matplotlib.pyplot as plt
from mrcnn.utils import compute_recall
from statistics import mean

plt.style.use('ggplot')

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Root directory of the project
    ROOT_DIR = os.path.abspath("../../")
    sys.path.append(ROOT_DIR)  # To find local version of the library
    from mrcnn import utils
    import mrcnn.model as modellib


if __name__ == '__main__':

    info = {'train': {
        'label_file_path': "dataset/elettrocablaggi_20200921/front_GRETA_230V/train/annots/labels.txt",
        'annotation_dir': "dataset/elettrocablaggi_20200921/front_GRETA_230V/train/annots/",
        'images_dir': "dataset/elettrocablaggi_20200921/front_GRETA_230V/train/images/"},
        'test': {'label_file_path': "dataset/elettrocablaggi_20200921/front_GRETA_230V/test/annots/labels.txt",
                 'annotation_dir': "dataset/elettrocablaggi_20200921/front_GRETA_230V/test/annots/",
                 'images_dir': "dataset/elettrocablaggi_20200921/front_GRETA_230V/test/images/"},
        'saved_model_dir': "weights/elettrocablaggi/GRETA_230V/"}

    inference_config = elettrocablaggi.ElettrocablaggiInferenceConfig()

    # create the model in inference mode
    model = modellib.MaskRCNN(mode="inference",
                              config=inference_config,
                              model_dir=info['saved_model_dir'])

    # Get path to saved weights
    # Either set a specific path or find last trained weights
    # model_path = os.path.join(ROOT_DIR, ".h5 file name here")
    model_path = model.find_last()

    # Load trained weights
    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)

    # Validation dataset
    dataset_val = elettrocablaggi.ElettrocablaggiDataset()
    class_info, val_image_info = dataset_val.load_elettrocablaggi(info['test']['label_file_path'],
                                                                  info['test']['annotation_dir'],
                                                                  info['test']['images_dir'])
    dataset_val.prepare()

    # Compute VOC-Style mAP @ IoU=0.5
    # Running on 10 images. Increase for better accuracy.
    # image_ids = np.random.choice(dataset_val.image_ids, 10)
    image_ids = dataset_val.image_ids
    APs = []
    ARs = []

    APs_75 = []
    ARs_75 = []

    APs_range = []
    ARs_range = []

    APs_small = []
    APs_big = []

    precisions = []
    recalls = []

    for image_id in image_ids:
        # Load image and cad data
        image, image_meta, gt_class_id, gt_bbox, gt_mask = \
            modellib.load_image_gt(dataset_val, inference_config,
                                   image_id)
        molded_images = np.expand_dims(modellib.mold_image(image, inference_config), 0)

        # Run object detection
        results = model.detect([image], verbose=0)
        r = results[0]

        print(f"########## Imagine {image_id} ##########")

        # Compute AP @0.5
        AP, prs, rls, _ = utils.compute_ap(gt_bbox, gt_class_id, gt_mask,
                                       r["rois"], r["class_ids"], r["scores"], r['masks'])
        APs.append(AP)
        precisions.append(prs)
        recalls.append(rls)

        # Compute recall @0.5
        recall, _ = compute_recall(r["rois"], gt_bbox)
        ARs.append(recall)

        # Compute AP @0.75
        AP, _, _, _ = utils.compute_ap(gt_bbox, gt_class_id, gt_mask,
                                       r["rois"], r["class_ids"], r["scores"], r['masks'], iou_threshold=0.75)
        APs_75.append(AP)

        # Compute recall @0.75
        recall, _ = compute_recall(r["rois"], gt_bbox, iou_threshold=0.75)
        ARs_75.append(recall)

        # Compute AP - range 0.55:0.05:0.95
        AP_range = utils.compute_ap_range(gt_bbox, gt_class_id, gt_mask,
                                          r["rois"], r["class_ids"], r["scores"], r['masks'], verbose=0)
        APs_range.append(AP_range)

        # # Compute AP - area 32x32
        AP_small, AP_big = utils.compute_ap_area(gt_bbox, gt_class_id, gt_mask,
                                                 r["rois"], r["class_ids"], r["scores"], r['masks'], verbose=0)
        APs_small.append(AP_small)
        APs_big.append(AP_big)

        # Compute Recall - range 0.55:0.05:0.95
        AR_range = utils.compute_recall_range(r["rois"], gt_bbox, verbose=0)
        ARs_range.append(AR_range)

    # folder where to save precision-recall curves
    prediction_dir = '/'.join(model_path.split('/')[:-1])

    # check if directory exist and the file is empty
    p_dir = os.path.join(prediction_dir, "prediction")
    if not os.path.isdir(p_dir):
        os.mkdir(p_dir)

    precisions = [*map(mean, zip(*precisions))]
    recalls = [*map(mean, zip(*recalls))]

    precisions.append(0)
    recalls.append(1)

    plt.plot(recalls, precisions, color='blue')
    plt.title('Precision-Recall curve')
    plt.ylabel('Precision')
    plt.xlabel('Recall')
    plt.tight_layout()
    plt.savefig(os.path.join(p_dir, 'pr-curve.jpg'))
    plt.close()

    print("########## Evaluation on test dataset ##########")
    print(f"mAP @0.5: {np.mean(APs): .3f}, with standard deviation: {np.std(APs): .3f}")
    print(f"mAR @0.5: {np.mean(ARs): .3f}, with standard deviation: {np.std(ARs): .3f}")

    print(f"mAP @0.75: {np.mean(APs_75): .3f}, with standard deviation: {np.std(APs_75): .3f}")
    print(f"mAR @0.75: {np.mean(ARs_75): .3f}, with standard deviation: {np.std(ARs_75): .3f}")

    print(f"mAP range [0.5:0.05:0.95]: {np.mean(APs_range): .3f}, with standard deviation: {np.std(APs_range): .3f}")
    print(f"mAR range [0.5:0.05:0.95]: {np.mean(ARs_range): .3f},"
          f" with standard deviation: {np.std(ARs_range): .3f}")

    print(f"mAP small area: {np.mean(APs_small): .3f}, with standard deviation: {np.std(APs_small): .3f}")
    print(f"mAP big area: {np.mean(APs_big): .3f}, with standard deviation: {np.std(APs_big): .3f}")

    print(f"Best AP: {max(APs): .3f} at Image: {APs.index(max(APs))}")
