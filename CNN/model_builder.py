from model_utils import load_data
from my_CNN_model import *
import cv2
import numpy as np

# Load training set
print('started loading')
X_train, y_train = load_data()
# X_train, y_train = np.random.randint(0, 100, (2, 96, 96, 1)), np.random.randint(0, 100, (2, 136))
print('loaded data')
if X_train.shape[0] == y_train.shape[0]:
    print('frames: ', X_train.shape[0])
# NOTE: Please check the load_data() method in utils.py to see how the data is preprocessed (normalizations and stuff)
# my_model = load_my_CNN_model('my_model')


# Setting the CNN architecture
my_model = get_my_CNN_model_architecture()
#
# # Compiling the CNN model with an appropriate optimizer and loss and metrics
compile_my_CNN_model(my_model, optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

# Training the model
hist = train_my_CNN_model(my_model, X_train, y_train)

# train_my_CNN_model returns a History object. History.history attribute is a record of training loss values and metrics
# values at successive epochs, as well as validation loss values and validation metrics values (if applicable).

# Saving the model
save_my_CNN_model(my_model, 'my_model')

'''
# You can skip all the steps above (from 'Setting the CNN architecture') after running the script for the first time.
# Just load the recent model using load_my_CNN_model and use it to predict keypoints on any face data
my_model = load_my_CNN_model('my_model')
'''
