import enum
import pandas as pd
import numpy as np
import sklearn.metrics as metrics
from imblearn.datasets import make_imbalance
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler, NearMiss
from sklearn import svm, tree
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler

RANDOM_STATE = 86


class BalancingMethod(enum.Enum):
    random_undersampling = 1
    SMOTE = 2
    near_miss = 3


class DatScaler(enum.Enum):
    standard_scaler = 1
    min_max_scaler = 2
    replace_negatives = 3


class MLModel(enum.Enum):
    log_reg = 1
    svm = 2
    knn = 3
    mn_naive_bayes = 4
    dec_tree = 5
    linear_reg = 6


class TripleRanker:

    def __init__(self, scaler_name='standard_scaler', model_name='log_reg', balancing_name='random_undersampling', sampling_strat=0.32):
        self.sampling_strat = sampling_strat
        if scaler_name == DatScaler.standard_scaler.name:
            self.scaler = StandardScaler()
        elif scaler_name == DatScaler.min_max_scaler.name:
            self.scaler = MinMaxScaler()
        elif scaler_name == DatScaler.replace_negatives.name :
            self.scaler = DatScaler.replace_negatives.name
        else:
            raise ValueError('Choose "standard_scaler".')
        if balancing_name == BalancingMethod.random_undersampling.name:
            self.balancer = RandomUnderSampler(sampling_strategy=self.sampling_strat, random_state=RANDOM_STATE) # 0.5: 1 negative, 1/2 positive
        elif balancing_name == BalancingMethod.SMOTE.name:
            self.balancer = SMOTE(sampling_strategy=self.sampling_strat)
        elif balancing_name == BalancingMethod.near_miss.name:
            self.balancer = NearMiss()
        elif not balancing_name:
            self.balancer = False
        if model_name == MLModel.log_reg.name:
            self.model = LogisticRegression()
        elif model_name == MLModel.svm.name:
            self.model = svm.SVC()
        elif model_name == MLModel.knn.name:
            self.model = KNeighborsClassifier(n_neighbors=3)
        elif model_name == MLModel.mn_naive_bayes.name:
            self.model = MultinomialNB()
        elif model_name == MLModel.dec_tree.name:
            self.model = tree.DecisionTreeClassifier()
        elif model_name == MLModel.linear_reg.name:
            self.model = LinearRegression()
        else:
            raise ValueError('Choose "log_reg", "svm", "knn", "mn_naive_bayes" or "dec_tree".')

    def training_of_triple_classifier(self, feature_set_path):
        if isinstance(feature_set_path, str):
            data_set = pd.read_pickle(feature_set_path)
        else:
            data_set = feature_set_path
        col = data_set.columns
        last_column = col[len(col)-1]
        print(data_set[last_column].value_counts())
        print('Positives', round(data_set[last_column].value_counts()[1] / len(data_set) * 100, 2), '% of the dataset')
        x = data_set.iloc[:, 1:len(col)-1]
        y = data_set.iloc[:, len(col)-1]
        if self.scaler == DatScaler.replace_negatives.name:
            features = x.columns
            new_x = pd.DataFrame()
            for feature in features:
                print(feature)
                this_feature = x[feature]
                print(this_feature[this_feature < 0])
                negative_values = len(this_feature[this_feature < 0])
                print(negative_values)
                if negative_values <= len(this_feature):
                    print('more positive values')
                    this_feature[this_feature < 0] = 0
                else:
                    print('more negative values')
                    this_feature[this_feature > 0] = 0
                new_x[feature] = this_feature
        else:
            x = self.scaler.fit_transform(x)
        if self.balancer:
            if isinstance(self.balancer, RandomUnderSampler):
                number_class_1 = data_set[last_column].value_counts()[0]
                number_class_2 = data_set[last_column].value_counts()[1]
                all_values = number_class_1 + number_class_2*2
                min_class_perc = (1/all_values)*number_class_2
                if self.sampling_strat > min_class_perc:
                    maj_class = number_class_2 * ((1 - (self.sampling_strat*2))/self.sampling_strat)
                    min_classes = number_class_2
                elif self.sampling_strat == min_class_perc:
                    maj_class = number_class_1
                    min_classes = number_class_2
                elif self.sampling_strat < min_class_perc:
                    raise ValueError('Minority class smaller than before')
                print(maj_class)
                print(min_classes)
                x, y = make_imbalance(x, y, sampling_strategy={0: int(maj_class), 1: int(min_classes), -1: int(min_classes)}, random_state=RANDOM_STATE)
            else:
                x, y = self.balancer.fit_resample(x, y)
        self.model.fit(x, y)
        return self.model

    def predict_triple_rankings(self, model, feature_set_without_rankings):
        if isinstance(feature_set_without_rankings, str):
            data_set = pd.read_pickle(feature_set_without_rankings)
        else:
            data_set = feature_set_without_rankings
        col = data_set.columns
        x = data_set.iloc[:, 1:len(col)]
        if self.scaler == DatScaler.replace_negatives.name:
            features = x.columns
            new_x = pd.DataFrame()
            for feature in features:
                print(feature)
                this_feature = x[feature]
                print(this_feature[this_feature < 0])
                negative_values = len(this_feature[this_feature < 0])
                print(negative_values)
                if negative_values <= len(this_feature):
                    print('more positive values')
                    this_feature[this_feature < 0] = 0
                else:
                    print('more negative values')
                    this_feature[this_feature > 0] = 0
                new_x[feature] = this_feature
        else:
            x = self.scaler.fit_transform(x)
        prediction = model.predict(x)
        data_set['rank_dist'] = prediction
        return data_set










