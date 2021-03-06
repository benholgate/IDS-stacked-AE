# -*- coding: utf-8 -*-
"""IDS_Sparse_Auto_Encoder.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1R7sc7dGT_s16wWZVR8vP3mKXOSZQp84b

## Intrusion Detection System: Sparse Autoencoder
"""

import warnings
warnings.filterwarnings('ignore')
import tensorflow as tf
import time
import itertools
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import confusion_matrix, accuracy_score,recall_score,precision_score,f1_score
import matplotlib.pyplot as plt
from matplotlib import pyplot
import numpy as np
import pandas as pd
import seaborn as sns
import math
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from scipy.stats import uniform
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier 
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.svm import SVC

from keras import models
from keras import layers
from keras.layers import Input,Dropout,Dense
from keras.models import Model
from keras import regularizers
from keras.utils.data_utils import get_file
from keras.constraints import maxnorm
from keras.optimizers import Adam, SGD, Adamax
from keras.regularizers import l1
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import load_model

df_train = pd.read_csv("train_imperson_without4n7_balanced_data_NOHEADINGS.csv") 
df_train.head(n=5)

df_test = pd.read_csv("test_imperson_without4n7_balanced_data_NOHEADINGS.csv") 
df_test.head(n=5)

df_train.shape

df_test.shape

x = df_train.drop(df_train.columns[152],axis=1)
y = df_train.iloc[:, [152]]
t = df_test.drop(df_test.columns[152],axis=1)
c = df_test.iloc[:, [152]]

c.shape

X = x.values
Y = y.values
T = t.values
C = c.values

# Pre-process data
from sklearn.preprocessing import StandardScaler, MinMaxScaler
scaler = MinMaxScaler()
scaler.fit(X)
trainX = scaler.transform(X) # train data set less target column
scaler.fit(T)
testT = scaler.transform(T) # test data set less target column

# Sparse Autoencoder 
learning_rate = 1e-3

inputs = Input(shape=(152, ))
encoded = Dense(100, activation='relu', activity_regularizer=regularizers.l1(learning_rate)) (inputs)
encoded = Dense(60, activation='relu', activity_regularizer=regularizers.l1(learning_rate)) (encoded)
code = Dense(20, activation='relu', activity_regularizer=regularizers.l1(learning_rate)) (encoded) 
decoded = Dense(60, activation='relu') (code)
decoded = Dense(100, activation='relu') (decoded)
output = Dense(152, activation='relu') (decoded)
autoencoder = Model(inputs, output)
autoencoder.compile(optimizer='sgd',  
                    loss='binary_crossentropy')                       

# plot the autoencoder
plot_model(autoencoder, 'autoencoder_no_compress.png', show_shapes=True)

# fit autoencoder model to reconstruct input
start = time.time()
history_stacked = autoencoder.fit(trainX, trainX, epochs=10, validation_data=(testT, testT), verbose=1, batch_size=20)
end = time.time()
running_time = end-start
print("Stacked AE took", running_time, "seconds")

# plot loss
pyplot.plot(history_stacked.history['loss'], label='train')
pyplot.plot(history_stacked.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

# define an encoder model (without the decoder)
encoder_stacked = Model(inputs, code)
plot_model(encoder_stacked, 'encoder_stacked_no_compress.png', show_shapes=True)

# save encoder to file
encoder_stacked.save('encoder.h5')

# Logistic Regression + Stacked Autoencoder
# load model from file
encoder_stacked = load_model('encoder.h5', compile =False)
# encode train data
trainX_encode = encoder_stacked.predict(trainX)
# encode test data
testT_encode = encoder_stacked.predict(testT)
# define the model
LR_model = LogisticRegression()
# fit model on train data set
start = time.time()
LR_model.fit(trainX_encode, Y)
# make predictions on test data set
yhat = LR_model.predict(testT_encode)
end = time.time()
running_time = end-start
print("Stacked AE with LR took", running_time, "seconds")

# Evaluate model
tn, fp, fn, tp=confusion_matrix(C, yhat).ravel()
Acc = (tp+tn)/(tp+tn+fp+fn)
DetRate = tp/(tp+tn)
Prec = tp/(tp+fp)
FAR = fp/(tn+fp)
FNR = fn/(fn+tp)
F1Score = (2*tp)/((2*fp)+fp+fn)
MCC = ((tp*tn)-(fp*fn))/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
print("Performance over the testing data set")
print("Accuracy : {} , Detection Rate : {} , Precision : {} , F1 : {}, FAR : {} , FNR : {}, MCC: {}".format(Acc,DetRate,Prec,F1Score,FAR, FNR, MCC ))

# Support Vector Machines (SVM) + Stacked Autoencoder
# load model from file
encoder_stacked = load_model('encoder.h5', compile =False)
# encode train data
trainX_encode = encoder_stacked.predict(trainX)
# encode test data
testT_encode = encoder_stacked.predict(testT)
# define the model
start = time.time()
SVC_model = SVC()
SVC_model.fit(trainX_encode, Y)
yhat = SVC_model.predict(testT_encode) 
end = time.time()
running_time = end-start
print("Stacked AE with SVM took", running_time, "seconds")
  
# Evaluate model
tn, fp, fn, tp=confusion_matrix(C, yhat).ravel()
Acc = (tp+tn)/(tp+tn+fp+fn)
DetRate = tp/(tp+tn)
Prec = tp/(tp+fp)
FAR = fp/(tn+fp)
FNR = fn/(fn+tp)
F1Score = (2*tp)/((2*fp)+fp+fn)
MCC = ((tp*tn)-(fp*fn))/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
print("Performance over the testing data set")
print("Accuracy : {} , Detection Rate : {} , Precision : {} , F1 : {}, FAR : {} , FNR : {}, MCC: {}".format(Acc,DetRate,Prec,F1Score,FAR, FNR, MCC ))

# Decision Tree (CART) + Stacked Autoencoder
# load model from file
encoder_stacked = load_model('encoder.h5', compile =False)
# encode train data
trainX_encode = encoder_stacked.predict(trainX)
# encode test data
testT_encode = encoder_stacked.predict(testT)
# define the model
CART_model = DecisionTreeClassifier()
# fit model on train data set
start = time.time()
CART_model.fit(trainX_encode, Y)
# make predictions on test data set
yhat = CART_model.predict(testT_encode)
end = time.time()
running_time = end-start
print("Stacked AE with CART took", running_time, "seconds")

# Evaluate model
tn, fp, fn, tp=confusion_matrix(C, yhat).ravel()
Acc = (tp+tn)/(tp+tn+fp+fn)
DetRate = tp/(tp+tn)
Prec = tp/(tp+fp)
FAR = fp/(tn+fp)
FNR = fn/(fn+tp)
F1Score = (2*tp)/((2*fp)+fp+fn)
MCC = ((tp*tn)-(fp*fn))/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
print("Performance over the testing data set")
print("Accuracy : {} , Detection Rate : {} , Precision : {} , F1 : {}, FAR : {} , FNR : {}, MCC: {}".format(Acc,DetRate,Prec,F1Score,FAR, FNR, MCC ))

# K-Nearest Neighbors (KNN) + Stacked Autoencoder
# load model from file
encoder_stacked = load_model('encoder.h5', compile =False)
# encode train data
trainX_encode = encoder_stacked.predict(trainX)
# encode test data
testT_encode = encoder_stacked.predict(testT)
# define the model
start = time.time()
KNN_model = KNeighborsClassifier(n_neighbors=1)
KNN_model.fit(trainX_encode, Y)
yhat = KNN_model.predict(testT_encode) 
end = time.time()
running_time = end-start
print("Stacked AE with KNN took", running_time, "seconds")
  
# Evaluate model
tn, fp, fn, tp=confusion_matrix(C, yhat).ravel()
Acc = (tp+tn)/(tp+tn+fp+fn)
DetRate = tp/(tp+tn)
Prec = tp/(tp+fp)
FAR = fp/(tn+fp)
FNR = fn/(fn+tp)
F1Score = (2*tp)/((2*fp)+fp+fn)
MCC = ((tp*tn)-(fp*fn))/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
print("Performance over the testing data set")
print("Accuracy : {} , Detection Rate : {} , Precision : {} , F1 : {}, FAR : {} , FNR : {}, MCC: {}".format(Acc,DetRate,Prec,F1Score,FAR, FNR, MCC ))

# Feature Selection -- Decision Tree

# load model from file
encoder_stacked = load_model('encoder.h5', compile =False)
# encode train data
trainX_encode = encoder_stacked.predict(trainX)
# encode test data
testT_encode = encoder_stacked.predict(testT)
# combine original train data matrix with encoder data matrix 
trainX_matrix = np.hstack((trainX, trainX_encode))

FS_model = ExtraTreesClassifier()
FS_model.fit(trainX_matrix, Y)
importances = FS_model.feature_importances_
print(FS_model.feature_importances_) 
#plot graph of feature importances for better visualization
feat_importances = pd.Series(FS_model.feature_importances_, index=np.argsort(importances)[::-1])
feat_importances.nlargest(20).plot(kind='barh')
plt.show()

# Create new array combining original data and new data produced by SAE

# load model from file
encoder_stacked = load_model('encoder.h5', compile=False)
# encode train data
trainX_encode = encoder_stacked.predict(trainX)
# encode test data
testT_encode = encoder_stacked.predict(testT)
# combine original train data matrix with encoder train data matrix 
trainX_matrix = np.hstack((trainX, trainX_encode))
# combine original test data matrix with encoder train  data matrix 
testT_matrix = np.hstack((testT, testT_encode))

# select top 20 features from combined train data set 
top20train = trainX_matrix[:, [53,101,44,78,56,93,84,59,109,60,0,66,89,120,58,96,123,125,103,162]]
 
# select top 20 features from combined test data set 
top20test = testT_matrix[:, [53,101,44,78,56,93,84,59,109,60,0,66,89,120,58,96,123,125,103,162]]

#top20train.shape
top20train.shape
#print(top20matrix[0])

print(trainX_matrix[0])

# Sparse Autoencoder -- Top 20 Features
learning_rate = 1e-1

inputs = Input(shape=(20, ))
encoded = Dense(15, activation='relu', activity_regularizer=regularizers.l1(learning_rate)) (inputs)
encoded = Dense(10, activation='relu', activity_regularizer=regularizers.l1(learning_rate)) (encoded)
code = Dense(5, activation='relu', activity_regularizer=regularizers.l1(learning_rate)) (encoded) 
decoded = Dense(10, activation='relu') (code)
decoded = Dense(15, activation='relu') (decoded)
output = Dense(20, activation='relu') (decoded)
autoencoder = Model(inputs, output)
autoencoder.compile(optimizer='sgd',  
                    loss='binary_crossentropy')   

# plot the autoencoder
plot_model(autoencoder, 'autoencoder_no_compress.png', show_shapes=True)

# fit autoencoder model to reconstruct input
start = time.time()
history20_stacked = autoencoder.fit(top20train, top20train,
                                    epochs=10,
                                    validation_data=(top20test, top20test),
                                    verbose=1, batch_size=20)
end = time.time()
running_time = end-start
print("Stacked AE top20 took", running_time, "seconds")

# plot loss
pyplot.plot(history20_stacked.history['loss'], label='train')
pyplot.plot(history20_stacked.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

# define an encoder model (without the decoder)
encoder20_stacked = Model(inputs, code)
plot_model(encoder20_stacked, 'encoder20_stacked_no_compress.png', show_shapes=True)
# save encoder to file
encoder20_stacked.save('encoder20.h5')

# Logistic Regression + Stacked Autoencoder
# with top 20 features

# load model from file
encoder20_stacked = load_model('encoder20.h5', compile =False)
# encode train data
top20train_encode = encoder20_stacked.predict(top20train)
# encode test data
top20test_encode = encoder20_stacked.predict(top20test)
# define the model
LR_model = LogisticRegression()
# fit model on train data set
start = time.time()
LR_model.fit(top20train_encode, Y)
# make predictions on test data set
yhat = LR_model.predict(top20test_encode)
end = time.time()
running_time = end-start
print("Stacked AE with LR top20 took", running_time, "seconds")

# Evaluate model
tn, fp, fn, tp=confusion_matrix(C, yhat).ravel() 
Acc = (tp+tn)/(tp+tn+fp+fn)
DetRate = tp/(tp+tn)
Prec = tp/(tp+fp)
FAR = fp/(tn+fp)
FNR = fn/(fn+tp)
F1Score = (2*tp)/((2*fp)+fp+fn)
MCC = ((tp*tn)-(fp*fn))/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
print("Performance over the testing data set")
print("Accuracy : {} , Detection Rate : {} , Precision : {} , F1 : {}, FAR : {} , FNR : {}, MCC: {}".format(Acc,DetRate,Prec,F1Score,FAR, FNR, MCC ))

# Support Vector Machines (SVM) + Stacked Autoencoder
# with top 20 features

# load model from file
encoder20_stacked = load_model('encoder20.h5', compile =False)
# encode train data
top20train_encode = encoder20_stacked.predict(top20train)
# encode test data
top20test_encode = encoder20_stacked.predict(top20test)
# define the model
SVC_model = SVC()
# fit model on train data set
start = time.time()
SVC_model.fit(top20train_encode, Y)
# make predictions on test data set
yhat = SVC_model.predict(top20test_encode)
end = time.time()
running_time = end-start
print("Stacked AE top20 took", running_time, "seconds")

# Evaluate model
tn, fp, fn, tp=confusion_matrix(C, yhat).ravel()
Acc = (tp+tn)/(tp+tn+fp+fn)
DetRate = tp/(tp+tn)
Prec = tp/(tp+fp)
FAR = fp/(tn+fp)
FNR = fn/(fn+tp)
F1Score = (2*tp)/((2*fp)+fp+fn)
MCC = ((tp*tn)-(fp*fn))/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
print("Performance over the testing data set")
print("Accuracy : {} , Detection Rate : {} , Precision : {} , F1 : {}, FAR : {} , FNR : {}, MCC: {}".format(Acc,DetRate,Prec,F1Score,FAR, FNR, MCC ))

# Decision Tree (CART) + Stacked Autoencoder
# with top 20 features

# load model from file
encoder20_stacked = load_model('encoder20.h5', compile =False)
# encode train data
top20train_encode = encoder20_stacked.predict(top20train)
# encode test data
top20test_encode = encoder20_stacked.predict(top20test)
# define the model
CART_model = DecisionTreeClassifier()
# fit model on train data set
start = time.time()
CART_model.fit(top20train_encode, Y)
# make predictions on test data set
yhat = CART_model.predict(top20test_encode)
end = time.time()
running_time = end-start
print("Stacked AE top20 with CART took", running_time, "seconds")

# Evaluate model
tn, fp, fn, tp=confusion_matrix(C, yhat).ravel() 
Acc = (tp+tn)/(tp+tn+fp+fn)
DetRate = tp/(tp+tn)
Prec = tp/(tp+fp)
FAR = fp/(tn+fp)
FNR = fn/(fn+tp)
F1Score = (2*tp)/((2*fp)+fp+fn)
MCC = ((tp*tn)-(fp*fn))/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
print("Performance over the testing data set")
print("Accuracy : {} , Detection Rate : {} , Precision : {} , F1 : {}, FAR : {} , FNR : {}, MCC: {}".format(Acc,DetRate,Prec,F1Score,FAR, FNR, MCC ))

# K-Nearest Neighbors (KNN) + Stacked Autoencoder
# with top 20 features

# load model from file
encoder20_stacked = load_model('encoder20.h5', compile =False)
# encode train data
top20train_encode = encoder20_stacked.predict(top20train)
# encode test data
top20test_encode = encoder20_stacked.predict(top20test)
# define the model
start = time.time()
KNN_model = KNeighborsClassifier(n_neighbors=1)
KNN_model.fit(top20train_encode, Y)
yhat = KNN_model.predict(top20test_encode) 
end = time.time()
running_time = end-start
print("Stacked AE top with KNN took", running_time, "seconds")

# Evaluate model
tn, fp, fn, tp=confusion_matrix(C, yhat).ravel() 
Acc = (tp+tn)/(tp+tn+fp+fn)
DetRate = tp/(tp+tn)
Prec = tp/(tp+fp)
FAR = fp/(tn+fp)
FNR = fn/(fn+tp)
F1Score = (2*tp)/((2*fp)+fp+fn)
MCC = ((tp*tn)-(fp*fn))/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
print("Performance over the testing data set")
print("Accuracy : {} , Detection Rate : {} , Precision : {} , F1 : {}, FAR : {} , FNR : {}, MCC: {}".format(Acc,DetRate,Prec,F1Score,FAR, FNR, MCC ))