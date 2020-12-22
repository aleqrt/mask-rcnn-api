"""
    L'oggetto component realizzato nelle regole DLV e' caratterizzato come segue

        x1,y1               x2,y2
            ----------------
            |              |
            |              |
            |              |
            |              |
            |              |
            |              |
            ----------------
        x3,y3               x4,y4


NOTA:
    - y2, x2 restituite dalla rete corrispondono a y4, x4 del disegno !!!!!!
    - TODO: passare da sistema XY di immagini a xy cartesiano per il calcolo delle posizioni con DLV !!!
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

    info = {'test': {'label_file_path': "dataset/elettrocablaggi_20200921/test/annots/labels.txt",
                     'annotation_dir': "dataset/elettrocablaggi_20200921/test/real/annots/",
                     'images_dir': "dataset/elettrocablaggi_20200921/test/real/images/"},
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

    samples = 5
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

        # create file and directory
        file_name = "facts_{}.txt".format(image_name[:-4])
        facts_dir = os.path.join("reasoner", "dlv_facts")
        dlv_output_name = "output_{}.txt".format(image_name[:-4])
        dlv_output_dir = os.path.join("reasoner", "dlv_output")
        dlv_program_name = 'neighborhood.asp'

        # check if directory exist and the file is empty
        if not os.path.isdir(facts_dir):
            os.mkdir(os.path.join("reasoner", "dlv_facts"))
        if glob.glob(os.path.join(facts_dir, file_name)):
            os.remove(os.path.join(facts_dir, file_name))
        if not os.path.isdir(dlv_output_dir):
            os.mkdir(os.path.join("reasoner", "dlv_output"))
        if glob.glob(os.path.join(dlv_output_dir, dlv_output_name)):
            os.remove(os.path.join(dlv_output_dir, dlv_output_name))

        # write facts for DLV reasoner in a txt file
        with open(os.path.join(facts_dir, file_name), "a") as f:
            for i in range(r['rois'].shape[0]):
                # NOTE: READ DESCRIPTION IN TOP OF FILE UNDERSTAND THE COORDINATES OF COMPONENT
                x3 = int(r['rois'][i, 1])
                y3 = int(r['rois'][i, 2])
                x4 = int(r['rois'][i, 3])
                y4 = int(r['rois'][i, 2])

                x1 = int(r['rois'][i, 1])
                y1 = int(r['rois'][i, 0])
                x2 = int(r['rois'][i, 3])
                y2 = int(r['rois'][i, 0])

                f.write('component("{}",{},{},{},{},{},{},{},{},{}). \n'.format(r['class_ids'][i] - 1, i + 1,
                                                                                x3, y3,
                                                                                x4, y4,
                                                                                x1, y1,
                                                                                x2, y2))
        os.system('./{} {} {} --filter=neighbour/5 > {}'
                  .format(os.path.join("reasoner", "dlv2"),
                          os.path.join(facts_dir, file_name),
                          os.path.join("reasoner", "encoding", dlv_program_name),
                          os.path.join(dlv_output_dir, dlv_output_name))
                  )

        # compute AP
        AP, precisions, recalls, overlaps = utils.compute_ap(gt_bbox, gt_class_id, gt_mask,
                                                             r["rois"], r["class_ids"], r["scores"], r['masks'])
        APs.append(AP)

    print("mAP: ", np.mean(APs))
