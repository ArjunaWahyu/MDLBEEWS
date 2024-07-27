import tensorflow as tf

model = tf.keras.models.load_model(
            'test\model_loc_mag.h5', compile=False)

print(model.summary())
