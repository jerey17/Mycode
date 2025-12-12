'''
classification_utils.py

This utility module is intended for use with the
    CS2PP L07_CS2PP_Data_Analysis.ipynb
and related notebooks for UoR CS2PP.

Contact: t.r.jones@reading.ac.uk
'''


import numpy as np
import matplotlib.pyplot as plt


def plot_decision_boundaries(X, y, start_index, model_class, ax=None, cmap=None, target_names=None, **model_params):
    """Function to plot the decision boundaries of a classification model.
    
    This uses just one pair columns of the data for fitting 
    the model, as we need to find the predicted value for every point in 
    scatter plot.
    
   
    Adopted from:
    http://scikit-learn.org/stable/auto_examples/ensemble/plot_voting_decision_regions.html
    http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_digits.html
    https://gist.github.com/anandology/772d44d291a9daa198d4
  
    
    Parameters
    ----------
    X : ndarray, of shape (n_samples, n_features)
        model input features
        NOTE: This routine selects two features.
              
    y : 1darray, of shape (n_samples)
        determines random number generation. The default is 0.
    start_index : int, position of the first of the pair of features to compare
    model_class : sklearn model class (e.g. LogisticRegression)
    ax : AxesSubplot, optional
        Destination for plot. The default is None.
    cmap : pyplot colormap, optional
    target_names: 2-element list of strings describing binary 
                  target labels
    model_params : kwargs passed to model_class

    Returns
    -------
    None.
    """
    
    # Handle defaults
    ax = ax or plt.gca()
    if cmap is None: cmap='viridis'
    if target_names is None: target_names = ['0', '1']
        
    # Data Reduction
    reduced_data = X[:, start_index: start_index+2]
    model = model_class(**model_params)
    model.fit(reduced_data, y)

    minx, miny = reduced_data.min(0)
    maxx, maxy = reduced_data.max(0)
    
    fixx = (maxx - minx) * 0.1
    fixy = (maxy - miny) * 0.1
    
    fig = plt.figure()
    nx, ny = 300, 300
    xs = np.linspace(minx-fixx, maxx+fixx, nx) # Range of values on x axis
    ys = np.linspace(miny-fixy, maxy+fixy, ny) # Range of values on y axis
    xx, yy = np.meshgrid(xs, ys)

    Z = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    
    ax.contourf(xx, yy, Z, alpha=0.4, cmap=cmap)
    uniq = set(y)
    for ync in uniq:
        ax.scatter(reduced_data[:, 0][y == ync], reduced_data[:, 1][y == ync], alpha=0.8, label=f'{target_names[ync]}')
    ax.legend()
    
    

def plot_svc_decision_function(model, ax=None, plot_support=True):
    """Plot the decision function for a 2D SVC
    numxxxx
    Parameters
    ----------
    model : sklearn model class (e.g. SVC)
    ax : AxesSubplot, optional
        Destination for plot. The default is None.
    cmap : pyplot colormap, optional
    plot_support: logical, optional
        Whether to plot support vectors

    Returns
    -------
    None.
    
    
    """
    if ax is None:
        ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    # create grid to evaluate model
    x = np.linspace(xlim[0], xlim[1], 30)
    y = np.linspace(ylim[0], ylim[1], 30)
    Y, X = np.meshgrid(y, x)
    xy = np.vstack([X.ravel(), Y.ravel()]).T
    
    # Main data to plot
    P = model.decision_function(xy).reshape(X.shape)
    
    # plot decision boundary and margins
    ax.contour(X, Y, P, colors='k',
               levels=[-1, 0, 1], alpha=0.5,
               linestyles=['--', '-', '--'])
    
    # plot support vectors
    if plot_support:
        ax.scatter(model.support_vectors_[:, 0],
                   model.support_vectors_[:, 1],
                   s=15, linewidth=1, facecolors='blue', zorder=2,
                   label='Support Vectors');
        ax.legend()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

