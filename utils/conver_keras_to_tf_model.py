import tensorflow as tf
import elettrocablaggi
import mrcnn.model as modellib


info = {'saved_model_dir': "weights/elettrocablaggi/0A00018253_04/"}

inf_config = elettrocablaggi.ElettrocablaggiInferenceConfig()

model = modellib.MaskRCNN(mode="inference",
                          config=inf_config,
                          model_dir=info['saved_model_dir'])

model.load_weights('weights/elettrocablaggi/0A00018253_04/mask_rcnn_elettrocablaggi_0149.h5', by_name=True)

export_path = './model/1'

tf.saved_model.save(model.keras_model, export_path)
