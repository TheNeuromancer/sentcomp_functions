from sklearn.metrics import roc_auc_score

def roc_auc_proba_scorer(y, y_pred):            
    score = roc_auc_score(y, y_pred[:,1])
    return score
''' 
Does the same as roc_auc_score but with the second column of the given y_pred.
This is done because the predict_proba method gives an array of shape [n_train * n_test * n_epochs * n_labels], which is equal to 2 even for a binary classification like here. The roc_auc scorer is therefore given a [n_epochs * 2] array, but can only manage to use a [n_epochs * 1].
'''