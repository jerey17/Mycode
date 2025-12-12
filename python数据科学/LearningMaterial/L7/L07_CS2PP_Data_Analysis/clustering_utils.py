'''
clustering_utils.py

This utility module is intended for use with the
    CS2PP L07_CS2PP_Data_Analysis.ipynb
and related notebooks for UoR CS2PP.

Contact: t.r.jones@reading.ac.uk
'''


import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from sklearn.datasets import make_blobs
from sklearn.metrics import pairwise_distances_argmin
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from scipy.stats import multivariate_normal
import seaborn as sns
from matplotlib.patches import Ellipse
import numpy.matlib as ml


def plot_kmeans(kmeans, X, n_clusters=4, rseed=0, cmap=None, ax=None):
    '''
    A method to visualise the areas of influence of each cluster centroid

    Parameters
    ----------
    kmeans : sklearn.cluster._kmeans.KMeans
        K-means model
    X : ndarray, of shape (n_samples, n_features)
        model input features
    n_clusters : int, optional
        Number of clusters. The default is 4.
    rseed : int, optional
        determines random number generation. The default is 0.
    cmap : pyplot colormap, optional
    ax : AxesSubplot, optional
        Destination for plot. The default is None.

    Returns
    -------
    None.

    '''
        
    # Handle defaults
    ax = ax or plt.gca()
    if cmap is None: cmap='viridis'
        
    # Run model, and get predictions
    labels = kmeans.fit_predict(X)
   
    
    # plot the input data
    ax.scatter(X[:, 0], X[:, 1], c=labels, s=20, cmap=cmap, zorder=2)

    # plot the representation of the KMeans model centroids
    centers = kmeans.cluster_centers_
    radii = [cdist(X[labels == i], [center]).max()
             for i, center in enumerate(centers)]
    for c, r in zip(centers, radii):
        ax.add_patch(plt.Circle(c, r, fc='#CCCCCC', lw=3, alpha=0.5, zorder=1))
    plt.gca().set_aspect('equal')



    
def generate_2d_gm(style=None):
    '''
    A method to plot 2D Gaussian Mixtures (generic examples)
    
    Parameters
    ----------
    style : str, optional
        type of plot to produce
    None: line contour
    heatmap: heatmap
    3d: 3D Surface
        
    Returns
    -------
    None.
    '''
    
    fig = plt.figure()
    nx, ny = 50, 50
    xs = np.linspace(-3.5,2.5,nx) # Range of values on x axis
    ys = np.linspace(-2,3,ny) # Range of values on y axis

    zs = np.zeros((nx,ny)) # z values -- height of the contour plot at each (x,y) location

    mean1 = [0.1,0.2]
    cv1 = np.identity(2)
    cv1[0,1] = 0.6
    cv1[1,0] = 0.6

    mean2 = [-2.0,1.0]
    cv2 = 0.3*np.identity(2)
    cv2[0,1] = -0.2
    cv2[1,0] = -0.2

    mean3 = [-0.3,1.7]
    cv3 = 0.2*np.identity(2)
    cv3[0,0] = 0.1

    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            z = 0.7*multivariate_normal(mean1,cv1).pdf([x,y]) \
                +0.2*multivariate_normal(mean2,cv2).pdf([x,y]) \
                +0.1*multivariate_normal(mean3,cv3).pdf([x,y])
            zs[j,i] = z

    # Plot contours of the mixture density 
    if style is None:
        plt.contour(xs, ys, zs)
        plt.gca().set_aspect('equal')
    elif style == 'heatmap':
        sns.heatmap(zs,xticklabels=False, yticklabels=False)
        plt.gca().invert_yaxis()
    elif style == '3d':
        X,Y = np.meshgrid(xs, ys)
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X,Y,zs,cmap=cm.coolwarm,linewidth=0,alpha=0.5)
        ax.contour(X,Y,zs)
    else:
        print('Named style must be one of: "heatmap" or "3d".')
    

def generate_2d_gmm(gmm, X, style=None):
    '''
    A method to plot 2D Gaussian Mixtures based on an sklearn model
    
    Parameters
    ----------
    gmm : an initialised and fit sklearn GaussianMixture model
    
    X : ndarray, Model input data, of shape (n_samples, n_features)
        model input features
    
    style : str, optional
        type of plot to produce
    None: line contour
    heatmap: heatmap
    3d: 3D Surface
        
    Returns
    -------
    None.
    '''
    
    K = len(gmm.weights_)
    
    minx, miny = X.min(0)
    maxx, maxy = X.max(0)
    
    fixx = (maxx - minx) * 0.1
    fixy = (maxy - miny) * 0.1
    
    fig = plt.figure()
    nx, ny = 50, 50
    xs = np.linspace(minx-fixx,maxx+fixx,nx) # Range of values on x axis
    ys = np.linspace(miny-fixy,maxy+fixy,ny) # Range of values on y axis

    zs = np.zeros((nx,ny)) # z values -- height of the contour plot at each (x,y) location

    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            z = 0
            for k in range(K):
                z += gmm.weights_[k]*multivariate_normal(gmm.means_[k], gmm.covariances_[k]).pdf([x,y])
            zs[j,i] = z

    # Plot contours of the mixture density 
    if style is None:
        plt.scatter(X[:, 0], X[:, 1], c=gmm.predict(X), cmap='Set2')
        plt.scatter(gmm.means_[:,0],gmm.means_[:,1],marker="x",c='r')
        plt.contour(xs, ys, zs)
        plt.gca().set_aspect('equal')
    elif style == 'heatmap':
        sns.heatmap(zs,xticklabels=False, yticklabels=False)
        plt.gca().invert_yaxis()
    elif style == '3d':
        X,Y = np.meshgrid(xs, ys)
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X,Y,zs,cmap=cm.coolwarm,linewidth=0,alpha=0.5)
        ax.contour(X,Y,zs)
    else:
        print('Named style must be one of: "heatmap" or "3d".')
    

def create_EM_plot():
    '''
    Original source: https://jakevdp.github.io/PythonDataScienceHandbook/06.00-figure-code.html#Expectation-Maximization
    
    The following figure shows a visual depiction of the Expectation-Maximization approach to K Means
    '''
    
    X, y_true = make_blobs(n_samples=300, centers=4,
                           cluster_std=0.60, random_state=0)

    rng = np.random.RandomState(42)
    centers = [0, 4] + rng.randn(4, 2)

    def draw_points(ax, c, factor=1):
        ax.scatter(X[:, 0], X[:, 1], c=c, cmap='viridis',
                   s=50 * factor, alpha=0.3)

    def draw_centers(ax, centers, factor=1, alpha=1.0):
        ax.scatter(centers[:, 0], centers[:, 1],
                   c=np.arange(4), cmap='viridis', s=200 * factor,
                   alpha=alpha)
        ax.scatter(centers[:, 0], centers[:, 1],
                   c='black', s=50 * factor, alpha=alpha)

    def make_ax(fig, gs):
        ax = fig.add_subplot(gs)
        ax.xaxis.set_major_formatter(plt.NullFormatter())
        ax.yaxis.set_major_formatter(plt.NullFormatter())
        return ax

    fig = plt.figure(figsize=(15, 4))
    gs = plt.GridSpec(4, 15, left=0.02, right=0.98, bottom=0.05, top=0.95, wspace=0.2, hspace=0.2)
    ax0 = make_ax(fig, gs[:4, :4])
    ax0.text(0.98, 0.98, "Random Initialization", transform=ax0.transAxes,
             ha='right', va='top', size=16)
    draw_points(ax0, 'gray', factor=2)
    draw_centers(ax0, centers, factor=2)

    for i in range(3):
        ax1 = make_ax(fig, gs[:2, 4 + 2 * i:6 + 2 * i])
        ax2 = make_ax(fig, gs[2:, 5 + 2 * i:7 + 2 * i])

        # E-step
        y_pred = pairwise_distances_argmin(X, centers)
        draw_points(ax1, y_pred)
        draw_centers(ax1, centers)

        # M-step
        new_centers = np.array([X[y_pred == i].mean(0) for i in range(4)])
        draw_points(ax2, y_pred)
        draw_centers(ax2, centers, alpha=0.3)
        draw_centers(ax2, new_centers)
        for i in range(4):
            ax2.annotate('', new_centers[i], centers[i],
                         arrowprops=dict(arrowstyle='->', linewidth=3, color='r'))


        # Finish iteration
        centers = new_centers
        ax1.text(0.95, 0.95, "E-Step", transform=ax1.transAxes, ha='right', va='top', size=14)
        ax2.text(0.95, 0.95, "M-Step", transform=ax2.transAxes, ha='right', va='top', size=14)


    # Final E-step    
    y_pred = pairwise_distances_argmin(X, centers)
    axf = make_ax(fig, gs[:4, -4:])
    draw_points(axf, y_pred, factor=2)
    draw_centers(axf, centers, factor=2)
    axf.text(0.98, 0.98, "Final Clustering", transform=axf.transAxes,
             ha='right', va='top', size=16)


    fig.savefig('Lecture_Images/sklEM.png', dpi=200)
    
    

def draw_ellipse(position, covariance, ax=None, **kwargs):
    """Draw an ellipse with a given position and covariance
    
    Source material: VanderPlas, Jake (2016). Python Data Science Handbook. O'Reilly Media, Inc. ISBN: 9781491912058
    """
    ax = ax or plt.gca()
    
    # Convert covariance to principal axes
    if covariance.shape == (2, 2):
        U, s, Vt = np.linalg.svd(covariance)
        angle = np.degrees(np.arctan2(U[1, 0], U[0, 0]))
        width, height = 2 * np.sqrt(s)
    else:
        angle = 0
        width, height = 2 * np.sqrt(covariance)
    
    # Draw the Ellipse
    for nsig in range(1, 4):
        ax.add_patch(Ellipse(position, nsig * width, nsig * height,
                             angle=angle, **kwargs))
        
def plot_gmm(gmm, X, label=True, ax=None):
    '''
    Source material: VanderPlas, Jake (2016). Python Data Science Handbook. O'Reilly Media, Inc. ISBN: 9781491912058
    '''
    
    ax = ax or plt.gca()
    labels = gmm.fit(X).predict(X)
    if label:
        ax.scatter(X[:, 0], X[:, 1], c=labels, s=10, cmap='Set2', zorder=2)
    else:
        ax.scatter(X[:, 0], X[:, 1], s=20, zorder=2)
    
    w_factor = 0.2 / gmm.weights_.max()
    for pos, covar, w in zip(gmm.means_, gmm.covariances_, gmm.weights_):
        draw_ellipse(pos, covar, alpha=w * w_factor)
    plt.gca().set_aspect('equal')
    
    

def elbow_point(data):
    '''
    Find Elbow Point, Trade off Point
    
    Source: https://stackoverflow.com/questions/2018178/finding-the-best-trade-off-point-on-a-curve/37121355#37121355
    
    Parameters
    ----------
        data: 1D array, float, elements sorted to represent a curve
        
    Returns
    -------
        idxOfBestPoint: int, the index of the point of maximum curvature
    '''
    
    
    curve = data
    nPoints = len(curve)
    allCoord = np.vstack((range(nPoints), curve)).T
    np.array([range(nPoints), curve])
    
    firstPoint = allCoord[0]
    lineVec = allCoord[-1] - allCoord[0]
    lineVecNorm = lineVec / np.sqrt(np.sum(lineVec**2))
    vecFromFirst = allCoord - firstPoint
    scalarProduct = np.sum(vecFromFirst * ml.repmat(lineVecNorm, nPoints, 1), axis=1)
    vecFromFirstParallel = np.outer(scalarProduct, lineVecNorm)
    vecToLine = vecFromFirst - vecFromFirstParallel
    distToLine = np.sqrt(np.sum(vecToLine ** 2, axis=1))
    idxOfBestPoint = np.argmax(distToLine)

    return idxOfBestPoint