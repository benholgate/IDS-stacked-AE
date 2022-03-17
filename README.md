# IDS-stacked-AE
## Aim
The aim of this project was to design a cyber threat detection system, or, more specifically, a predictive model that can distinguish "good" traffic from "bad" traffic. 
The Intrusion Detection System (IDS) is within the context of the vulnerability of IoT enabled devices.
## Dataset
The dataset used was the Aegean WiFi Intrusion Dataset (AWID), which was prepared and managed by George Mason University and the University of 
the Aegean, and which has real traces of both normal and intrusive IEEE 802.11 traffic. The AWID training data set consists of 97,044 observations and the testing set 40,158 observations. 
Both data sets had the input features numbered 4 and 7 removed because they provide temporal information that may cause unfair prediction. As a result, both data sets had 153 features, consisting 
of 152 prediction features and one target feature (normal or attack).
## Stacked Autoencoder
I developed a stacked autoencoder (SAE), which is an unsupervised deep neural network, as the representational learner, using Python, TensorFlow, and Keras.
The SAE in the has input layer with 152 inputs (the number of prediction features), followed by a hidden layer (or encoder) with 100 neurons, a central hidden layer of 50 neurons, another hidden layer (or decoder) with 100 neurons, 
and finally an output layer with 152 neurons.  
## Feature Selection
The SAE performed automatic feature extraction to reduce the dimensions of the processed data. The 152 features from both the AWID’s training and testing data sets were fed into the SAE. As a result, 
the SAE extracted an additional 50 new features with new data instances that were appended to both the original training and testing sets. This resulted in a larger data set with 202 features.
A feature importance technique, the Extremely Randomized Trees Classifier (ExtraTreesClassifier), was used to determine the most relevant features from the combined data set. The feature selection was set to identify the top 20 features from the combined data set.
Around half of these top 20 features were abstract features from the new training set, which suggests that the SAE was able to successfully extract features that are relevant to the attack class with 
meaningful representations.
## Hyperparameter Tuning
Scikit-Learn’s GridSearchCV was used to determine the optimal values of certain hyperparameters that are too complex to test manually. After experimentation, the optimal configuration was found to be:
3 hidden layers;
100 neurons in the encoder and decoder hidden layers, and 50 neurons in the central hidden layer;
SGD optimizer;
relu activation;
binary cross-entropy loss function;
0.001 learning rate.
## Classification Algorithms
Logistic Regression (LR) and Support Vector Machines (SVM) resulted in the highest accuracy rates, of just over 98%, although LR was musch faster in terms of time taken to build the model. The LR-SAE and SVM-SAE models performed as well as other studies on the AWID database in regard to accuracy.
