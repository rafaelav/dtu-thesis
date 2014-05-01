'''
Created on May 1, 2014

@author: rafa
'''
from sklearn import datasets
from sklearn import cross_validation
from sklearn import svm
from sklearn import hmm
import numpy as np


def state_transitions(matrix, loc_count):
        model = hmm.GaussianHMM(loc_count, "full")
        #print(matrix_with_bssids_on_columns)
        X = np.array(matrix)
        model.fit([X])
        Z = model.predict(X)
        return Z
    
# X = np.array([[5, 6, 1], [8, 9, 2], [5, 6, 1], [8, 9, 2]])
# y = np.array([1, 2, 3, 4])
X = [[1,1,1,0,0,0],
[1,1,1,0,0,0],
[1,1,0,0,0,0],
[0,0,0,1,1,1],
[0,0,0,1,1,0],
[0,0,0,1,1,1],
[0,0,1,1,1,0],
[0,0,1,1,1,0]]
 
max_score = 0.0
for loc in range(2,5):
    y = state_transitions(X, loc)
    y = np.array(y).tolist()
    print("Locations: "+str(loc))
    print(y)
     
    kf = cross_validation.KFold(len(X), n_folds=2)
      
    print(kf)
    
    X = np.array(X)
    y = np.array(y)
    
    clf = svm.SVC(kernel='linear', C=1)
    scores = cross_validation.cross_val_score(clf, X, y, cv=4)

    print(scores)
    avg_score = 0.0
    for x in scores:
        avg_score = avg_score + x
    avg_score = avg_score/len(scores)
    
    if avg_score > max_score:
        max_score = avg_score
        min_loc = loc
  
print(max_score,min_loc)
    
"""    # k fold
    folds_score = []
    for train_index, test_index in kf:
        print("TRAIN:", train_index, "TEST:", test_index)
        X = np.array(X)
        y = np.array(y)
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        X_train = np.array(X_train).tolist()
        X_test = np.array(X_test).tolist()
        y_train = np.array(y_train).tolist()
        y_test = np.array(y_test).tolist()
  
        print(X_train, X_test)
        print(y_train, y_test)
          
        # cross validation
        clf = svm.SVC(kernel='linear', C=1).fit(X_train, y_train)
        score = clf.score(X_test, y_test)
#     clf = svm.SVC(kernel='linear', C=1)
#     scores = cross_validation.cross_val_score(clf, X, y, cv=2)
        folds_score.append(score)
        print(folds_score)
#print(scores)  
    avg_score = 0.0
    for x in folds_score:
        avg_score = avg_score + x
    avg_score = avg_score/len(folds_score)
    print("Avg score: ",avg_score)    
      
    if avg_score>max_score:
        max_score = avg_score
        min_loc = loc
  
print(min_loc)"""

# iris = datasets.load_iris()
# print(iris.data)
# print(iris.target)
# 
# kf = cross_validation.KFold(len(X), n_folds=2)
#      
# print(kf)
#      
# for train_index, test_index in kf:
#     print("TRAIN:", train_index, "TEST:", test_index)
#     X = np.array(X)
#     y = np.array(y)
#     X_train, X_test = X[train_index], X[test_index]
#     y_train, y_test = y[train_index], y[test_index]
# clf = svm.SVC(kernel='linear', C=1).fit(X_train, y_train)
# print(clf.score(X_test, y_test))