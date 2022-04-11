"""- TODO: passare da sistema XY di immagini a xy cartesiano per il calcolo delle posizioni con DLV !!!
            Per ora il reasoner calcola correttamente RIGHT e LEFT, ma inverte TOP e BOTTOM.

    - class_ids contiene l'indice di dataset_val.class_names corrispondente alla label del componente
    - dataset_val.class_names: ['BG', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    - come è strutturato l'output della rete
            results: [{'rois': array([[y1, x1, y2, x2],
                                    [y1, x1, y2, x2]], dtype=int32),
                       'class_ids': array([...], dtype=int32),
                       'scores': array([...], dtype=float32),
                       'masks': array([ [ [] ] ])}]
"""

import glob
import os
import sys
import warnings
import numpy as np
import matplotlib.pyplot as plt
import elettrocablaggi

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Root directory of the project
    ROOT_DIR = os.path.abspath("../../")
    sys.path.append(ROOT_DIR)  # To find local version of the library
    from mrcnn import visualize
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

    info = {'test': {'label_file_path': "dataset/elettrocablaggi_20200921/GRETA_230V/test/annots/labels.txt",
                     'annotation_dir': "dataset/elettrocablaggi_20200921/GRETA_230V/test/annots/",
                     'images_dir': "dataset/elettrocablaggi_20200921/GRETA_230V/test/images/"},
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

    samples = 2
    random = False
    replace = False
    single = False

    if random:
        # Test on a random image
        image_ids = np.random.choice(dataset_val.image_ids, samples, replace=replace)
    elif single:
        # Test on 1 images
        image_ids = [0]
    else:
        # Test on all validation images
        image_ids = dataset_val.image_ids

    # folder where to save predicted images (the same of the model weights)
    prediction_dir = '/'.join(model_path.split('/')[:-1])

    for image_id in image_ids:
        # load original image
        original_image, image_meta, gt_class_id, gt_bbox, gt_mask = modellib.load_image_gt(dataset_val,
                                                                                           inference_config,
                                                                                           image_id)

        # infer on original image
        results = model.detect([original_image], verbose=1)
        r = results[0]

        # draw result of net masks on the original image
        fig, ax = get_ax()
        masked_image = visualize.display_instances(original_image, r['rois'], r['masks'], r['class_ids'],
                                                   dataset_val.class_names, r['scores'], ax=ax)

        # write the image with bounding boxes and masks to file
        image_name = dataset_val.source_image_link(image_id).split('/')[-1]

        # check if directory exist and the file is empty
        p_dir = os.path.join(prediction_dir, "prediction")
        if not os.path.isdir(p_dir):
            os.mkdir(p_dir)

        fig.savefig(os.path.join(p_dir, image_name))
        plt.close(fig)

        # # create file and directory
        # net_dir = os.path.join("reasoner", "net_demo")
        # file_name = "{}_net.asp".format(image_name[:-4])
        # dlv_output_name = "{}_output_net.asp".format(image_name[:-4])
        # dlv_program_name = 'encoding.asp'
        #
        # # check if directory exist and the file is empty
        # if not os.path.isdir(net_dir):
        #     os.mkdir(os.path.join("reasoner", "net_demo"))
        # if glob.glob(os.path.join(net_dir, file_name)):
        #     os.remove(os.path.join(net_dir, file_name))
        # if glob.glob(os.path.join(net_dir, dlv_output_name)):
        #     os.remove(os.path.join(net_dir, dlv_output_name))
        #
        # # write facts for DLV reasoner in a txt file
        # with open(os.path.join(net_dir, file_name), "a") as f:
        #     for i in range(r['rois'].shape[0]):
        #         # NOTE: READ DESCRIPTION IN TOP OF FILE UNDERSTAND THE COORDINATES OF COMPONENT
        #         xs = int(min(r['rois'][i, 1], r['rois'][i, 3]))
        #         ys = int(min(r['rois'][i, 0], r['rois'][i, 2]))
        #
        #         xd = int(max(r['rois'][i, 1], r['rois'][i, 3]))
        #         yd = int(max(r['rois'][i, 0], r['rois'][i, 2]))
        #
        #         f.write('net("{}",{},{},{},{},{}). \n'.format(r['class_ids'][i] - 1, i + 1,
        #                                                       xs, ys,
        #                                                       xd, yd))
