import os
import sys
import warnings
import numpy as np
import matplotlib.pyplot as plt
import elettrocablaggi

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Root directory of the project
    ROOT_DIR = os.path.abspath("../../")
    sys.path.append(ROOT_DIR)  # To find local version of the library
    from mrcnn import visualize
    from mrcnn import utils
    import mrcnn.model as modellib


def get_ax(rows=1, cols=1, size=8):
    """Return a Matplotlib Axes array to be used in
    all visualizations in the notebook. Provide a
    central point to control graph sizes.
    
    Change the default size attribute to control the size
    of rendered images
    """
    fig, ax = plt.subplots(rows, cols, figsize=(size * cols, size * rows))
    return fig, ax


if __name__ == '__main__':

    info = {'train': {'label_file_path': "dataset/elettrocablaggi_20200921/train/annots/labels.txt",
                      'annotation_dir': "dataset/elettrocablaggi_20200921/train/annots/",
                      'images_dir': "dataset/elettrocablaggi_20200921/train/images/"},
            'test': {'label_file_path': "dataset/elettrocablaggi_20200921/test/annots/labels.txt",
                     'annotation_dir': "dataset/elettrocablaggi_20200921/test/annots/",
                     'images_dir': "dataset/elettrocablaggi_20200921/test/images/"},
            'saved_model_dir': "weights/elettrocablaggi_20200921/"}

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

    random = False
    samples = 5
    replace = False

    if random:
        # Test on a random image
        image_ids = np.random.choice(dataset_val.image_ids, samples, replace=replace)
    else:
        # Test on all validation images
        image_ids = dataset_val.image_ids

    # folder where to save predicted images (the same of the model weights)
    prediction_dir = '/'.join(model_path.split('/')[:-1])

    APs = []
    for image_id in image_ids:
        # load original image
        original_image, image_meta, gt_class_id, gt_bbox, gt_mask = modellib.load_image_gt(dataset_val,
                                                                                           inference_config,
                                                                                           image_id,
                                                                                           use_mini_mask=False)

        # infer on original image
        results = model.detect([original_image], verbose=1)
        r = results[0]

        # draw result of inferred masks on the original image
        fig, ax = get_ax()
        masked_image = visualize.display_instances(original_image, r['rois'], r['masks'], r['class_ids'],
                                                   dataset_val.class_names, r['scores'], ax=ax)

        # write the image with bounding boxes and masks to file
        image_name = dataset_val.source_image_link(image_id).split('/')[-1]
        print("saving inferred image in ", prediction_dir + '/' + image_name)
        fig.savefig(prediction_dir + '/' + image_name)
        plt.close(fig)

        # compute AP
        AP, precisions, recalls, overlaps = utils.compute_ap(gt_bbox, gt_class_id, gt_mask,
                                                             r["rois"], r["class_ids"], r["scores"], r['masks'])
        print("AP:", AP)
        print("precision:", precisions)
        print("recall:", recalls)
        print("overlap:", overlaps)
        APs.append(AP)

        print("\n\n")

    print("mAP: ", np.mean(APs))
