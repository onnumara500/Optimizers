# -*- coding: utf-8 -*-
"""optimizers.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1cs5OLLA_Av1lfcQwMWYYge2ojPdhxCur
"""

import numpy as np
from scipy.optimize import minimize
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
import csv

# Define the problem parameters
n = 5
mu = np.array([
    8.6033358901938017e-01, 3.4256184594817283e+00, 6.4372981791719468e+00,
    9.5293344053619631e+00, 1.2645287223856643e+01, 1.5771284874815882e+01,
    1.8902409956860023e+01, 2.2036496727938566e+01, 2.5172446326646664e+01,
    2.8309642854452012e+01, 3.1447714637546234e+01, 3.4586424215288922e+01,
    3.7725612827776501e+01, 4.0865170330488070e+01, 4.4005017920830845e+01,
    4.7145097736761031e+01, 5.0285366337773652e+01, 5.3425790477394663e+01,
    5.6566344279821521e+01, 5.9707007305335459e+01, 6.2847763194454451e+01,
    6.5988598698490392e+01, 6.9129502973895256e+01, 7.2270467060308960e+01,
    7.5411483488848148e+01, 7.8552545984242926e+01, 8.1693649235601683e+01,
    8.4834788718042290e+01, 8.7975960552493220e+01, 9.1117161394464745e+01
])

def objective(x):
    return np.sum(x**2)

def rho(x, mu):
    n = len(x)
    result = np.zeros(30)
    for j in range(30):
        exp_term = np.exp(-mu[j]**2 * np.sum(x**2))
        sum_term = sum(2 * (-1)**(ii-1) * np.exp(-mu[j]**2 * np.sum(x[ii-1:]**2)) for ii in range(2, n+1))
        result[j] = -(exp_term + sum_term + (-1)**n) / mu[j]**2
    return result

def A(mu_val):
    return 2 * np.sin(mu_val) / (mu_val + np.sin(mu_val) * np.cos(mu_val))

#y?
def constraint(x, mu, A):
    r = rho(x, mu)
    term1 = sum(sum(
        mu[i]**2 * mu[j]**2 * A[i] * A[j] * r[i] * r[j] *
        (np.sin(mu[i]+mu[j])/(mu[i]+mu[j]) + np.sin(mu[i]-mu[j])/(mu[i]-mu[j]))
        for j in range(i+1, 30)) for i in range(30))
    term2 = sum(
        mu[j]**4 * A[j]**2 * r[j]**2 *
        (np.sin(2*mu[j])/(2*mu[j]) + 1)/2
        for j in range(30))
    term3 = sum(
        mu[j]**2 * A[j] * r[j] *
        (2*np.sin(mu[j])/mu[j]**3 - 2*np.cos(mu[j])/mu[j]**2)
        for j in range(30))
    return term1 + term2 - term3 + 2/15 - 0.0001


def generate_data(x, radius):
    X = []
    y = []
    for _ in range(100):
        delta = np.random.uniform(-radius, radius, n)
        x_new = x + delta
        X.append(x_new)
        y.append(constraint(x_new, mu, A(mu)))
    return np.array(X), np.array(y)

"""def fit_regression_model(X, y):
    # Create a polynomial features object (degree=2 for quadratic)
    poly_features = PolynomialFeatures(degree=2, include_bias=False)

    # Create a pipeline that first creates polynomial features, then applies linear regression
    model = make_pipeline(poly_features, LinearRegression())

    # Fit the model
    model.fit(X, y)

    return model"""

def fit_regression_model(X, y):
    model = LinearRegression()
    model.fit(X, y)
    return model

def trust_region_optimization(x0, max_iterations=100, initial_radius=0.01):
    x = x0
    radius = initial_radius
    results = []
    for iteration in range(max_iterations):
        # Generate data and fit regression model
        X, y = generate_data(x, radius)
        model = fit_regression_model(X, y)

        # Define the subproblem
        def subproblem_objective(delta):
            return objective(x + delta)

        def subproblem_constraint(delta):
            delta_reshaped = np.array([x + delta])  # Reshape for prediction
            return model.predict(delta_reshaped)[0]  # Constraint learned from regression

        # Solve the subproblem using SLSQP
        res = minimize(subproblem_objective, np.zeros(n), method='SLSQP',
                       constraints={'type': 'ineq', 'fun': subproblem_constraint},
                       bounds=[(-radius, radius)] * n,
                       options={'ftol': 1e-8, 'maxiter': 1000})


        delta = res.x
        # Update x and radius
        x = x + delta
        radius = min(2 * radius, 5.0)  # Increase trust region radius

        results.append((iteration, objective(x), x, subproblem_constraint(delta)))


    return results
# Run the optimization
x0 = np.random.randn(n)
results = trust_region_optimization(x0)

# Save results to CSV
with open('optimization_results_polynomial.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Iteration', 'Objective Value'] + [f'x{i+1}' for i in range(n)] + ['Constraint Value'])
    for iteration, obj_value, x, constraint_value in results:
        writer.writerow([iteration, obj_value] + list(x) + [constraint_value])

print("Optimization complete. Results saved to 'optimization_results.csv'.")