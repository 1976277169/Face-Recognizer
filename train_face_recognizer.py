"""
/*****************************************************
 *
 *              Gabor Vecsei
 * Email:       vecseigabor.x@gmail.com
 * Blog:        https://gaborvecsei.wordpress.com/
 * LinkedIn:    www.linkedin.com/in/vecsei-gabor
 * Github:      https://github.com/gaborvecsei
 *
 *****************************************************/
"""

import json
import os
import sys
import time

import cv2
import numpy as np

# Read the settings file
with open('settings_for_recognition.json') as settings_file:
    settings = json.load(settings_file)

# Here we store the cropped faces ready for training
trainFolder = settings['output_folder']

if not os.path.isdir(trainFolder) or not os.path.exists(trainFolder):
    print "Couldn't find the train folder where we store the prepared images!"
    sys.exit(1)

trainImages = []
# Labels for training
labels = []
# Person names
people = []

"""
EXAMPLE (for the labelling):

trainImages = [...the images...]
labels = [0,1,2,3,4,5,6,7,8,9,...]
people = [Gabor,Gabor,Gabor,Gabor,Gabor,Mona,Mona,Mona,Mona,Mona]

So When a prediction returns 6 we will know that that's people[6] (Which is Mona)
"""

i = 0
for subFolder in os.listdir(trainFolder):
    subFolderPath = os.path.join(trainFolder, subFolder)
    if os.path.isdir(subFolderPath):
        for imageName in os.listdir(trainFolder + "/" + subFolder):
            imageExtension = imageName.split('.')[-1]
            # Check if we use an actual image
            if imageExtension in ['jpg', 'png', 'jpeg', 'bmp']:
                imagePath = os.path.join(trainFolder, subFolder, imageName)
                # Read the image in Grayscale
                imageGray = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
                imageGray = cv2.equalizeHist(imageGray)
                # It has to be the same size, so resize all of the images (AxA square image)
                imageGrayResized = cv2.resize(imageGray,
                                              (settings['resize_for_training'], settings['resize_for_training']))
                # Add the resized image to the training set
                trainImages.append(np.asarray(imageGrayResized, dtype=np.uint8))
                # We need numbers
                labels.append(i)
                # The folder name is the person's name too so append it to the names
                people.append(subFolder)
                i += 1

# Convert to numpy array
labels = np.asarray(labels, dtype=np.int32)

# The data is prepared and we can train our recognizer
print "Starting the training"
startTime = time.clock()

model = cv2.createEigenFaceRecognizer()
model.train(trainImages, labels)

print "Training is completed in: " + str(time.clock() - startTime) + " secs!"

answer = raw_input("Would you like to save the trained model?(y/n)\n")

if answer == 'y' or answer == 'Y':
    # Save the model in order to use it for recognition
    model.save(settings['saved_model_path'])
    # Save the people array to know which number is which name
    np.save(settings['name_array_path'], people)
    print "The model is saved: " + settings['saved_model_path']
    print "The name array is saved: " + settings['name_array_path']
    print "Training is completed!\nNow you can use it!"
else:
    print "The trained model is not saved!"
