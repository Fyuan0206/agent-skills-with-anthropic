# Question Examples by Subject Area

Domain-specific examples to guide question generation for common machine learning topics.

## Machine Learning Fundamentals

### Types of Learning

**True/False Examples**:

- "In supervised learning, the model learns from labeled data where each input has a corresponding output." (True)
- "Unsupervised learning requires labeled data to identify patterns in the dataset." (False)
- "Reinforcement learning involves an agent learning through trial and error with rewards and penalties." (True)

**Explanatory Examples**:

- "Explain the key differences between supervised, unsupervised, and reinforcement learning. Provide an example application for each."
- "Describe what makes a problem suitable for classification versus regression. How do the outputs differ?"

### Overfitting and Underfitting

**True/False Examples**:

- "A model that performs well on training data but poorly on test data is overfitting." (True)
- "Increasing model complexity always improves generalization performance." (False)
- "An underfitting model has high bias and low variance." (True)

**Explanatory Examples**:

- "Explain the bias-variance tradeoff. How does model complexity affect each component?"
- "Describe three techniques to prevent overfitting in machine learning models."

---

## Linear Algebra for Machine Learning

### Vectors and Operations

**True/False Examples**:

- "The dot product of two perpendicular vectors is zero." (True)
- "The Euclidean norm of a vector represents its magnitude or length." (True)
- "Matrix multiplication is commutative: $AB = BA$ for all matrices A and B." (False)

**Explanatory Examples**:

- "Explain why the dot product is useful for measuring similarity between feature vectors. How does cosine similarity relate to this?"
- "Describe the geometric interpretation of matrix-vector multiplication as a linear transformation."

**Coding Example**:

```latex
\textbf{Question: Euclidean Distance Calculation}

Implement a function to calculate the Euclidean distance between two points represented as NumPy arrays.

\begin{enumerate}
    \item Take two vectors of equal length as input
    \item Compute the element-wise difference
    \item Square each difference, sum them, and take the square root
    \item Return the distance as a scalar
\end{enumerate}
```

---

## Data Preprocessing

### Feature Scaling

**True/False Examples**:

- "Standardization transforms features to have zero mean and unit variance." (True)
- "Feature scaling is essential for decision trees to work correctly." (False - trees are scale-invariant)
- "Min-max normalization scales features to a range of [0, 1]." (True)

**Explanatory Examples**:

- "Explain why K-Nearest Neighbors requires feature scaling but Decision Trees do not. What property of each algorithm causes this difference?"
- "Compare standardization (z-score normalization) and min-max normalization. When would you prefer one over the other?"

**Coding Example**:

```latex
\textbf{Question: Implement Standardization}

Implement a function to standardize a feature matrix (zero mean, unit variance).

\begin{enumerate}
    \item Calculate the mean of each feature (column)
    \item Calculate the standard deviation of each feature
    \item Subtract the mean and divide by the standard deviation
    \item Handle the edge case where standard deviation is zero
\end{enumerate}
```

**Use Case Example**:

- "You have a dataset with features: age (20-80), income ($20K-$500K), and number of children (0-5). Before applying KNN, you need to preprocess the data. Implement standardization and explain why this is necessary for distance-based algorithms."

---

## Model Evaluation

### Train/Test Split and Cross-Validation

**True/False Examples**:

- "Using the same data for training and evaluation gives an accurate estimate of model performance." (False)
- "K-fold cross-validation provides a more robust estimate of model performance than a single train/test split." (True)
- "The test set should never be used during model selection or hyperparameter tuning." (True)

**Explanatory Examples**:

- "Explain why we need separate training, validation, and test sets. What role does each play in the model development process?"
- "Describe how 5-fold cross-validation works. What are its advantages over a simple holdout method?"

### Classification Metrics

**True/False Examples**:

- "Accuracy is always the best metric for evaluating classification models." (False - especially for imbalanced data)
- "Precision measures the proportion of positive predictions that are actually correct." (True)
- "A model with high recall may have low precision if it predicts many false positives." (True)

**Explanatory Examples**:

- "Explain the difference between precision and recall. In what scenarios would you prioritize one over the other?"
- "Describe what a confusion matrix shows and how to calculate accuracy, precision, recall, and F1-score from it."

**Coding Example**:

```latex
\textbf{Question: Implement Confusion Matrix Metrics}

Given predicted and true labels, compute classification metrics from scratch.

\begin{enumerate}
    \item Count True Positives (TP), False Positives (FP), True Negatives (TN), and False Negatives (FN)
    \item Calculate accuracy: (TP + TN) / (TP + TN + FP + FN)
    \item Calculate precision: TP / (TP + FP)
    \item Calculate recall: TP / (TP + FN)
    \item Calculate F1-score: 2 * (precision * recall) / (precision + recall)
\end{enumerate}
```

**Use Case Example**:

```latex
\textbf{Question: Credit Card Fraud Detection Evaluation}

\textbf{Scenario:}
A bank has deployed a fraud detection model. Out of 10,000 transactions, 50 are actually fraudulent. The model flagged 80 transactions as fraud, correctly identifying 40 actual fraud cases.

\textbf{Task:}
1. Construct the confusion matrix
2. Calculate accuracy, precision, recall, and F1-score
3. Explain why accuracy alone is misleading for this problem
4. Recommend which metric the bank should prioritize and why
```

---

## K-Nearest Neighbors (KNN)

### Algorithm Fundamentals

**True/False Examples**:

- "KNN is a lazy learning algorithm because it does not build an explicit model during training." (True)
- "The time complexity of KNN prediction is O(1) because there is no training phase." (False - prediction is O(nm) where n is samples and m is features)
- "Increasing k in KNN always improves model accuracy." (False - there is an optimal k)
- "KNN can be used for both classification and regression tasks." (True)

**Explanatory Examples**:

- "Explain why KNN is called a 'lazy learner' or 'instance-based learner.' What are the implications for training and prediction time?"
- "Describe the curse of dimensionality and explain why it particularly affects KNN. What happens to distances as dimensionality increases?"
- "Compare the effect of small k versus large k on the bias-variance tradeoff in KNN."

### Distance Metrics

**True/False Examples**:

- "Euclidean distance is the only distance metric that can be used with KNN." (False)
- "Manhattan distance sums the absolute differences along each dimension." (True)
- "Cosine similarity measures the angle between two vectors rather than their magnitude." (True)

**Explanatory Examples**:

- "Compare Euclidean and Manhattan distance. In what situations might Manhattan distance be preferred?"
- "Explain when cosine similarity would be a better choice than Euclidean distance for measuring similarity between data points."

**Coding Example**:

```latex
\textbf{Question: Implement KNN Classifier}

Implement K-Nearest Neighbors classification from scratch.

\begin{enumerate}
    \item Calculate Euclidean distances from the test point to all training points
    \item Find the indices of the k smallest distances
    \item Retrieve the labels of the k nearest neighbors
    \item Return the most common label (majority vote)
    \item Test with different values of k
\end{enumerate}

\textbf{Function Signature:}
\begin{verbatim}
def knn_classify(X_train, y_train, x_test, k):
    """
    Classify a single test point using KNN.

    Args:
        X_train: Training features (n_samples, n_features)
        y_train: Training labels (n_samples,)
        x_test: Test point (n_features,)
        k: Number of neighbors

    Returns:
        Predicted class label
    """
\end{verbatim}
```

**Use Case Example**:

```latex
\textbf{Question: Iris Species Classification}

\textbf{Scenario:}
A botanist wants to automatically classify iris flowers into three species based on measurements of sepal length, sepal width, petal length, and petal width.

\textbf{Data:}
Use sklearn's iris dataset:
\begin{verbatim}
from sklearn.datasets import load_iris
iris = load_iris()
X, y = iris.data, iris.target
\end{verbatim}

\textbf{Task:}
1. Split data into training (70%) and testing (30%)
2. Standardize the features
3. Find the optimal k using 5-fold cross-validation (try k = 1, 3, 5, 7, 9)
4. Plot training and validation accuracy vs k to visualize the bias-variance tradeoff
5. Report the test accuracy with the optimal k

\textbf{Hints:}
\begin{itemize}
    \item Use StandardScaler from sklearn.preprocessing
    \item Use cross_val_score with cv=5 for cross-validation
    \item Small k leads to overfitting, large k leads to underfitting
\end{itemize}
```

---

## Decision Trees

### Tree Structure and Splitting

**True/False Examples**:

- "Decision trees split data based on feature values to create homogeneous subsets." (True)
- "Gini impurity measures the probability of misclassifying a randomly chosen element." (True)
- "Decision trees require feature scaling to work properly." (False - trees are scale-invariant)
- "A decision tree with no depth limit will always achieve 100% training accuracy." (True - if features can distinguish all samples)

**Explanatory Examples**:

- "Explain how a decision tree chooses which feature to split on at each node. What role does Gini impurity or information gain play?"
- "Describe the geometric interpretation of decision tree boundaries. Why are they always axis-aligned?"
- "Explain why deep decision trees tend to overfit and how pruning or limiting tree depth helps prevent this."

### Tree Hyperparameters

**True/False Examples**:

- "Limiting the maximum depth of a decision tree can help prevent overfitting." (True)
- "A minimum samples split of 1 would allow the tree to grow until each leaf has one sample." (True)
- "Decision trees can only handle categorical features, not continuous ones." (False)

**Explanatory Examples**:

- "Describe how the max_depth hyperparameter affects the bias-variance tradeoff in decision trees."
- "Explain the difference between pre-pruning (stopping criteria) and post-pruning techniques."

**Coding Example**:

```latex
\textbf{Question: Calculate Gini Impurity}

Implement a function to calculate the Gini impurity of a node.

\begin{enumerate}
    \item Count the frequency of each class in the node
    \item Calculate the proportion of each class: $p_c = n_c / n_{total}$
    \item Compute Gini: $G = 1 - \sum_{c} p_c^2$
    \item Test on example: [0, 0, 1, 1, 1] should give Gini = 0.48
\end{enumerate}

\textbf{Function Signature:}
\begin{verbatim}
def gini_impurity(labels):
    """
    Calculate Gini impurity for a set of labels.

    Args:
        labels: Array of class labels

    Returns:
        Gini impurity value between 0 and 0.5 (for binary)
    """
\end{verbatim}
```

**Use Case Example**:

```latex
\textbf{Question: Loan Default Prediction}

\textbf{Scenario:}
A bank wants to predict whether loan applicants will default based on their credit history, income, and loan amount. The model should be interpretable so loan officers can explain decisions to applicants.

\textbf{Data:}
\begin{verbatim}
import numpy as np
import pandas as pd

np.random.seed(42)
n = 500

data = {
    'credit_score': np.random.randint(300, 850, n),
    'annual_income': np.random.exponential(50000, n),
    'loan_amount': np.random.exponential(15000, n),
    'debt_ratio': np.random.uniform(0, 0.8, n)
}
df = pd.DataFrame(data)

# Higher default probability with low credit, high debt ratio
default_prob = 0.1 + 0.3 * (df['credit_score'] < 600) + 0.2 * (df['debt_ratio'] > 0.5)
df['default'] = (np.random.random(n) < default_prob).astype(int)
\end{verbatim}

\textbf{Task:}
1. Train a decision tree classifier with max_depth=3
2. Visualize the tree structure
3. Identify the most important feature for predicting default
4. Explain three decision rules the tree has learned
5. Discuss why a shallow tree might be preferred for this application

\textbf{Hints:}
\begin{itemize}
    \item Use sklearn.tree.plot_tree() or export_text() to visualize
    \item Feature importances are available via tree.feature_importances_
    \item Consider the tradeoff between accuracy and interpretability
\end{itemize}
```

---

## Linear Models

### Linear Regression

**True/False Examples**:

- "Linear regression finds the line that minimizes the sum of squared residuals." (True)
- "Linear regression can model non-linear relationships if polynomial features are added." (True)
- "The coefficients in linear regression represent the change in output for a one-unit change in the corresponding feature." (True)

**Explanatory Examples**:

- "Explain the geometric interpretation of linear regression. What does the regression line represent in feature space?"
- "Describe how adding polynomial features transforms a linear model into a non-linear one. What are the risks of using high-degree polynomials?"

### Logistic Regression

**True/False Examples**:

- "Despite its name, logistic regression is used for classification, not regression." (True)
- "Logistic regression outputs probabilities between 0 and 1 using the sigmoid function." (True)
- "The decision boundary of logistic regression is always linear in the original feature space." (True)

**Explanatory Examples**:

- "Explain why we use the sigmoid function in logistic regression instead of a linear function. What problem does it solve?"
- "Describe how to interpret the coefficients of a logistic regression model. What do the odds ratios tell us?"

**Coding Example**:

```latex
\textbf{Question: Implement the Sigmoid Function}

Implement the sigmoid function and use it to convert logistic regression outputs to probabilities.

\begin{enumerate}
    \item Implement: $\sigma(z) = \frac{1}{1 + e^{-z}}$
    \item Handle numerical overflow for large negative values of z
    \item Given weights w and bias b, compute P(y=1|x) = sigmoid(w·x + b)
    \item Convert probabilities to class predictions using threshold 0.5
\end{enumerate}
```

---

## Regularization

### Ridge and Lasso Regression

**True/False Examples**:

- "Regularization adds a penalty term to the loss function to prevent overfitting." (True)
- "Ridge regression (L2) tends to shrink coefficients toward zero but rarely makes them exactly zero." (True)
- "Lasso regression (L1) can perform feature selection by setting some coefficients to exactly zero." (True)
- "Increasing the regularization parameter lambda always improves model performance." (False)

**Explanatory Examples**:

- "Compare Ridge (L2) and Lasso (L1) regularization. When would you choose one over the other?"
- "Explain how the regularization parameter lambda affects the bias-variance tradeoff. What happens at extreme values of lambda?"

**Use Case Example**:

```latex
\textbf{Question: Housing Price Prediction with Regularization}

\textbf{Scenario:}
You're building a model to predict housing prices with many features (size, bedrooms, location scores, etc.). Some features may be highly correlated or irrelevant.

\textbf{Task:}
1. Train Linear Regression, Ridge, and Lasso models
2. Use cross-validation to find optimal lambda for Ridge and Lasso
3. Compare the coefficients across models
4. Identify which features Lasso eliminated (set to zero)
5. Compare test RMSE for all three models

\textbf{Hints:}
\begin{itemize}
    \item Use sklearn.linear_model (LinearRegression, Ridge, Lasso)
    \item Use RidgeCV and LassoCV for automatic lambda selection
    \item Standardize features before regularization
\end{itemize}
```

---

## Tips for Different Lecture Topics

### For Algorithm-Heavy Lectures (KNN, Decision Trees)

- Focus coding question on implementing the core algorithm
- Use case should show practical application with real-world data
- T/F questions test edge cases, complexity, and hyperparameters

### For Theory-Heavy Lectures (Bias-Variance, Evaluation)

- More explanatory questions testing conceptual understanding
- T/F questions test common misconceptions
- Coding question computes metrics or demonstrates concepts
- Use case demonstrates why theory matters in practice

### For Math-Heavy Lectures (Linear Algebra, Optimization)

- T/F questions test mathematical properties
- Explanatory questions connect math to ML applications
- Coding question implements mathematical operations
- Use case shows how math enables ML solutions

### For Preprocessing Lectures (Scaling, Encoding)

- T/F questions test when preprocessing is necessary
- Explanatory questions compare different techniques
- Coding question implements preprocessing from scratch
- Use case shows impact of preprocessing on model performance
