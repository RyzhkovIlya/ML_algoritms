import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import recall_score, precision_score, precision_recall_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

class LogisticRegressionGD:
    def __init__(self,
                penalty:str=None,
                random_state:int=None):
        """_summary_

        Args:
            penalty (str, optional): _description_. Defaults to None.
            random_state (int, optional): _description_. Defaults to None.
        """
        method_list = ['l1', 'l2', 'elasticnet', None]
        assert \
            (penalty is None)|(penalty in method_list), \
            f'This method not found. Please give one of this method {method_list}. Receive method = {penalty}'
        assert\
            (isinstance(random_state, int))|(random_state is None),\
            f'N_iterations must be only integer and > 0. Receive {type(random_state)} = {random_state}.'
        
        self.__random_state = random_state
        self.__penalty = penalty
        np.random.seed(seed=self.__random_state)
    
    def __check_params(self,
                        X):
        """Check input params
        """
        assert\
            (isinstance(self.__learning_rate, float))|(isinstance(self.__learning_rate, int))&(self.__learning_rate>0)&(self.__learning_rate<=1),\
            f'Learning_rate must be only in interval (0, 1]. Receive {self.__learning_rate}.'
        assert\
            isinstance(self.__n_iterations, int)&(self.__n_iterations>0),\
            f'N_iterations must be only integer and > 0. Receive {type(self.__n_iterations)} = {self.__n_iterations}.'
        assert\
            isinstance(self.__C, float)|isinstance(self.__C, int),\
            f'C must be only integer or float. Receive {type(self.__C)}.'
        assert\
            (X.shape[0]>0)&(X.shape[1]>0),\
            f'X must not be empty.'
        assert\
            (isinstance(self.__batch_size, int))|(self.__batch_size is None),\
            f'Batch_size must be only integer or None and >0. Receive {self.__batch_size}.'
        
    def __sigmoid(self, 
                X):
        """Activation function - sigmoid
        Args:
            X (array-like): Training samples
        Returns:
            _type_: probability after passing through sigmoid
        """
        # Calculate sigmoid
        return 1 / (1 + np.exp(-X))
    
    def __net_input(self,
                    X):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Computes the weighted sum of inputs
        return np.dot(self.coef_.T, X) + self.intercept_

    def __probability(self, 
                        X):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Returns the probability after passing through sigmoid
        return self.__sigmoid(self.__net_input(X=X))

    def __calculate_gradient(self, 
                            X):
        """_summary_
        """
        # If the usual linear regression we find the gradient, lasso, ridge and elastic
        self.__dW = -1*(np.dot(X, self.__residuals))/self.__m if self.__penalty == None else \
            (-1*((np.dot(X, self.__residuals))+(self.__C*np.abs(self.coef_)))/self.__m if self.__penalty == 'l1' else \
                (-1*((np.dot(X, self.__residuals))+(2*self.__C*self.coef_))/self.__m if self.__penalty == 'l2' else 
                    (-1*(np.dot(X, self.__residuals))+(self.__C*np.abs(self.coef_))+(2*self.__C*self.coef_))/self.__m))
        
        # Find the gradient for the free term b
        self.__db = -2*np.sum(self.__residuals)/self.__m

    def __update_weights(self,
                            X,
                            y):
        """Update weights and b
        """
        # Get probability result
        y_pred = self.__probability(X=X)
        y_pred = y_pred.reshape((y_pred.shape[1],1))

        # Deviation from the true value
        self.__residuals = y - y_pred

        cost = -1*np.mean(y*np.log10(y_pred) + (1-y)*np.log10(1-y_pred))
        self.cost_list.append(cost)

        # stop condition
        if (len(self.cost_list)>2):
            self.__flag = False if np.sum(self.__residuals) < -10e30 else True
        else:
            pass

        # Calculate gradients  
        self.__calculate_gradient(X=X)
        gradients = {"derivative_weight": self.__dW,"derivative_bias": self.__db}

        # Update the weights with the gradient found from the production MSE
        self.coef_ -= (self.__learning_rate*gradients["derivative_weight"])
        # Update free member b
        self.intercept_ -= self.__learning_rate * gradients["derivative_bias"]

    def plot_cost(self):
        """Show loss curve
        """
        len_cost = len(self.cost_list)
        spl = 10
        if len_cost < spl:
            spl = len_cost
        plt.plot(range(0, len_cost, len_cost//spl), self.cost_list[::len_cost//spl])
        plt.xticks(range(0, len_cost, len_cost//spl), rotation='vertical')
        plt.xlabel("Number of Iteration")
        plt.ylabel("Cost")
        plt.show()

    def __initialize_weights_and_bias(self,
                                        X)->tuple:
        """Create a matrix for the weights of each attribute and the free member bias


        Args:
            X: array-like, shape = [n_features, n_samples]

        Returns:
            tuple: Weights and bias matrixs
        """
        weights = np.random.rand(X.shape[0], 1)
        bias = np.random.random()
        return weights, bias
    
    def fit(self, 
            X:pd.DataFrame or np.ndarray, 
            y:pd.Series or np.ndarray,
            batch_size:int=None,
            learning_rate:float=0.001,
            C:float=1.0,
            max_n_iterations:int=1000,
            ):
        """Fit the training data

        Args:
            X (_type_): _description_
            y (_type_): _description_
            batch_size: Number of batches
            learning_rate (float, optional): _description_. Defaults to 0.001.
            C (float, optional): _description_. Defaults to 1.0.
            max_n_iterations (int, optional): _description_. Defaults to 1000.
            stop_cost (float, optional): _description_. Defaults to 0.1.

        Returns:
            _type_: _description_
        """
        self.__learning_rate = learning_rate
        self.__n_iterations = max_n_iterations
        self.__C = C
        self.__batch_size = batch_size
        self.__flag = True
        self.cost_list = []

        # Check correct params
        self.__check_params(X=X)
        if isinstance(X, np.ndarray)==False:
            X = np.array(X)
        X = X.T
        y = np.array(y)
        assert\
            (y.shape[0]==X.shape[1]),\
            f'Y shape must be equal X shape.'
        y = y.reshape((y.shape[0], 1))

        # Create a matrix for the weights of each attribute and free member bias
        self.coef_, self.intercept_ = self.__initialize_weights_and_bias(X=X)

        # Dimensionality of features and number of training examples
        self.n_features_in_, self.__m = X.shape

        for _ in range(self.__n_iterations):
            if self.__flag:
                if self.__batch_size is not None:
                    for i in range((self.__m-1)//self.__batch_size + 1):
                        # Defining batches.
                        start_i = i*self.__batch_size
                        end_i = start_i + self.__batch_size
                        xb = X[:,start_i:end_i]
                        yb = y[start_i:end_i]
                        # Updating the weights
                        self.__update_weights(X=xb,
                                        y=yb)
                else:
                    # Updating the weights
                    self.__update_weights(X=X,
                                        y=y)
            else:
                break
        return self
    
    def predict(self, X):
        """ Predicts the value after the model has been trained.
        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Test samples
        Returns
        -------
        Predicted value
        """

        # Check correct params
        self.__check_params(X=X)
        if isinstance(X, np.ndarray)==False:
            X = np.array(X)
        return self.__probability(X=X.T).flatten()

#Read data
seed = 42
X, y = make_classification(n_samples=1000,n_features=5)
# data = pd.read_csv('data.csv', header=None)
# x, y = data.iloc[:, :-1], data.iloc[:, -1]

#Normalization
scaler = StandardScaler()
X = scaler.fit_transform(X)
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# x_train = pd.DataFrame(x_train)
#Use class LogisticRegressionGD

log_reg = LogisticRegressionGD(penalty='l2',
                                random_state=42) # l1, l2, elasticnet
log_reg.fit(X = x_train, 
            y = y_train, 
            C = 0.01, 
            learning_rate=0.01, 
            max_n_iterations=2000,
            batch_size=128)

# Find optimal threshhold
precisions, recalls, thresholds = precision_recall_curve(y_train, log_reg.predict(x_train))
f_scores = np.nan_to_num((2*precisions*recalls)/(precisions+recalls+0.0001))
f_max_index = np.argmax(f_scores)
custom_threshold = thresholds[f_max_index]

#get predict
pred = log_reg.predict(X = x_test)
pred = (pred>custom_threshold).astype(int)

#Metrics
print('precision', precision_score(y_test, pred))
print('recall', recall_score(y_test, pred), '\n')

#Check sklearn model
sk_model = LogisticRegression(C = 0.01, 
                                max_iter=2000, 
                                random_state=42,
                                penalty='l2')
sk_model.fit(X=x_train, y = y_train)
sk_pred = sk_model.predict(x_test)
print('SKLEARN PREDICT')
print('precision', precision_score(y_test, sk_pred))
print('recall', recall_score(y_test, sk_pred))