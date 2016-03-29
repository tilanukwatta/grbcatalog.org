import csv
import numpy as np
from sklearn import svm
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import StratifiedKFold
from sklearn.metrics import roc_curve, auc
from scipy import interp
from sklearn import datasets
import matplotlib.pyplot as plt
import scipy.optimize as optimization
import pandas
import sys
import shutil
import os
import random
from scipy.stats import rankdata

cpath = os.getcwd() + '/'
missing_val = -1000.0

#machine_z_data_file = '/home/tilan/Desktop/Dropbox/django/grbcatalog/grbcatalog/machine-z/grb_data_sample_num_284_f25.csv'
machine_z_data_file = '/web_app/grbcatalog/grbcatalog/machine-z/grb_data_sample_num_284_f25.csv'

def func(x, c, m):
    return c + m * x

def read_from_file(filename):
    infile = open(filename, 'r')
    #csv.register_dialect('format', delimiter=',', quoting=csv.QUOTE_NONE, skipinitialspace=True)
    datareader = csv.reader(infile)
    data = []
    for row in datareader:
        #print row
        data.append(row)
    infile.close()
    data_header = data[0]
    data = data[1:]
    predictors = []
    response = []
    for row in data:
        num = len(row)
        #print row
        #import ipdb;ipdb.set_trace() # debugging code
        predictor_row = []
        for r in row[:num-1]:
            try:
                val = float(r)
            except ValueError:
                val = missing_val
            predictor_row.append(val)
        predictors.append(predictor_row)
        #predictors.append([float(r) for r in row[:num-1]])
        response.append(float(row[num-1]))
    return np.array(predictors), np.array(response)

def read_from_file_old(filename):
    infile = open(filename, 'r')
    #csv.register_dialect('format', delimiter=',', quoting=csv.QUOTE_NONE, skipinitialspace=True)
    datareader = csv.reader(infile)
    data = []
    for row in datareader:
        #print row
        data.append(row)
    infile.close()
    data_header = data[0]
    data = data[1:]
    predictors = []
    response = []
    for row in data:
        num = len(row)
        print row
        predictors.append([float(r) for r in row[:num-1]])
        response.append(float(row[num-1]))
    return np.array(predictors), np.array(response)

def get_sim_data():
    sim_num = 250
    x1 = np.random.random_integers(0, 10, sim_num)
    x2 = np.random.random_integers(0, 10, sim_num)
    x3 = np.random.random_integers(0, 10, sim_num)
    x4 = np.random.random_integers(0, 10, sim_num)
    x5 = np.random.random_integers(0, 10, sim_num)
    #a = [0.5, 0.25, 0.3, 0.1, 0.8]
    a = [1., 1., 1., 1., 1.]
    predictors = []
    response = []
    for k in range(sim_num):
        predictors.append([x1[k], x2[k], x3[k], x4[k], x5[k]])
        val = a[0]*x1[k]+a[1]*x2[k]+a[2]*x3[k]+a[3]*x4[k]+a[4]*x5[k]
        val = val + np.random.randn() * 6.0
        response.append(val)
    return np.array(predictors), np.array(response)

def xyplot(x, y, xmin, xmax, ymin, ymax, title, xlabel, ylabel, plot_name, line):
    plt.subplots_adjust(hspace=0.4)
    ax = plt.subplot(111)
    if (line==1):
        ax.plot(x, y, 'r', linewidth=2)
        ax.plot([0., 100.], [0., 100.], 'b', linewidth=1)
    else:
        ax.plot(x, y, 'ro')
        ax.plot([0., 100.], [0., 100.], 'b', linewidth=1)

    if (xmin < xmax):
        ax.set_xlim(xmin, xmax)
    if (ymin < ymax):
        ax.set_ylim(ymin, ymax)

    #"""
    fit = optimization.curve_fit(func, np.array(x), np.array(y))[0]
    c = fit[0]
    m = fit[1]
    yfit = []
    for k in x:
        yfit.append(func(k, c, m))
    ax.plot(x, yfit, 'g')
    print m, c
    #"""

    #ax.axhline(linewidth=axis_width, color="k")
    #ax.axvline(linewidth=axis_width, color="k")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    #plt.show()
    plt.savefig(plot_name)
    plt.clf()

def xyploterr(x, y, yerr, xmin, xmax, ymin, ymax, title, xlabel, ylabel, plot_name, fit):
    plt.subplots_adjust(hspace=0.4)
    ax = plt.subplot(111)

    #ax.plot(x, y, 'ro')
    ax.errorbar(x, y, yerr=yerr, fmt='o')
    ax.plot([0., 100.], [0., 100.], 'k--', linewidth=1)

    if (xmin < xmax):
        ax.set_xlim(xmin, xmax)
    if (ymin < ymax):
        ax.set_ylim(ymin, ymax)

    if fit==1:
        fit, fitcov = optimization.curve_fit(func, np.array(x), np.array(y), sigma=np.array(yerr), absolute_sigma=False)
        fiterr = np.sqrt(np.diag(fitcov))
        c = fit[0]
        cerr = fiterr[0]
        m = fit[1]
        merr = fiterr[1]
        print 'm: ', m, '  c: ', c
        yfit = []
        for k in x:
            yfit.append(func(k, c, m))
        ax.plot(x, yfit, 'g')
        print m, c

    #ax.axhline(linewidth=axis_width, color="k")
    #ax.axvline(linewidth=axis_width, color="k")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    #plt.show()
    plt.savefig(plot_name, bbox_inches='tight')
    plt.clf()

def histogram(x, bin_num, xmin, xmax, ymin, ymax, title, xlabel, ylabel, plot_name, y_log=0):

    plt.subplots_adjust(hspace=0.4)
    ax = plt.subplot(111)

    if (y_log == 1):
        n, bins, patches = ax.hist(x, bin_num, facecolor='green', alpha=0.75, log=True)
    else:
        n, bins, patches = ax.hist(x, bin_num, facecolor='green', alpha=0.75)

    if (xmin < xmax):
        ax.set_xlim(xmin, xmax)
    if (ymin < ymax):
        ax.set_ylim(ymin, ymax)

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.savefig(cpath + plot_name)
    plt.clf()

def histogram_2d(x, y, bin_num, xmin, xmax, ymin, ymax, title, xlabel, ylabel, plot_name, y_log=0):

    plt.subplots_adjust(hspace=0.4)
    ax = plt.subplot(111)

    if (y_log == 1):
        H = ax.hist2d(x, y, bins=bin_num)
    else:
        H = ax.hist2d(x, y, bins=bin_num)

    # plots cool hexagonals
    #im = ax.hexbin(x, y, gridsize=50)
    #plt.colorbar(im, ax=ax)

    plt.colorbar(H[3], ax=ax)

    if (xmin < xmax):
        ax.set_xlim(xmin, xmax)
    if (ymin < ymax):
        ax.set_ylim(ymin, ymax)

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.savefig(plot_name)
    plt.clf()

def corr(x, y):
    values = np.array([x, y], float)
    corr = np.corrcoef(values)
    #import ipdb; ipdb.set_trace() # debugging code
    return corr[0][1]

def ml_engine(predictors, response, request, ntree = 100, nodesize = 3, mtry = 4, random_seed = 999, weights=[]):
    clf = RandomForestRegressor(n_estimators = ntree,
                                criterion='mse',  # this is the only one available (mse-mean squared error)
                                min_samples_leaf = nodesize,
                                max_features = mtry,
                                random_state = random_seed)
    #print len(predictors), len(response), len(weights)
    if len(weights) > 0:
        clf.fit(predictors, response, sample_weight=weights)
    else:
        clf.fit(predictors, response)

    return clf.predict(request)[0]

def plot_almost_all_traning(predictors, response, ntree = 100, nodesize = 3, mtry = 4, random_seed = 999, weights=[]):
    num = len(predictors)
    num_repeat = num
    index = set(range(num))

    x = []
    y = []
    num_sample = int(num * 0.5)

    for i in range(num_repeat):
        #pick = set(np.random.random_integers(0, num-1, 1))
        pick = set([i])
        rest = index - pick
        #rest = random.sample(rest, num_sample)
        print pick
        print rest
        x.append(response[list(pick)][0])
        if len(weights) > 0:
            request = ml_engine(predictors[list(rest)], response[list(rest)], predictors[list(pick)],
                            ntree = ntree, nodesize = nodesize, mtry = mtry, random_seed = random_seed, weights=weights[list(rest)])
        else:
            request = ml_engine(predictors[list(rest)], response[list(rest)], predictors[list(pick)],
                            ntree = ntree, nodesize = nodesize, mtry = mtry, random_seed = random_seed)
        y.append(request)
        #print x, y
        #import ipdb; ipdb.set_trace() # debugging code
        #y.append(clf.predict(predictors[i]))


    fit = optimization.curve_fit(func, np.array(x), np.array(y))[0]
    c = fit[0]
    m = fit[1]
    print 'm: ', m, '  c: ', c
    yCorrected = []
    for k in y:
        val = (k - c)/m
        yCorrected.append(val)

    corr_val = corr(x, y)
    statistics_str = "(Correlation Coefficient : {0:.3})".format(corr_val)
    #xyplot(x, y, 0, 10, 2.9, 3.02, "Redshift Predictor " + statistics_str, "Redshift", "Predicted Redshift", "almost_all_correlation.pdf", 0)
    xyplot(x, y, 0, 10, min(y), max(y), "Redshift Predictor " + statistics_str, "Redshift", "Predicted Redshift", "almost_all_correlation.pdf", 0)

    #import ipdb; ipdb.set_trace() # debugging code
    corr_val = corr(x, yCorrected)
    statistics_str = "(Correlation Coefficient : {0:.3})".format(corr_val)
    #xyplot(x, yCorrected, 0, 10, 0, 10, "Redshift Predictor " + statistics_str, "Redshift", "Predicted Redshift", "almost_all_correlation_corrected.pdf", 0)
    xyplot(x, yCorrected, 0, 10, 0, 10, "Redshift Predictor (Corrected) " + statistics_str, "Redshift", "Predicted Redshift", "almost_all_correlation_corrected.pdf", 0)

    histogram_2d(x, yCorrected, 25, 0.0, 10.0, 0.0, 10.0, "Machine-z " + statistics_str, "log Redshift", "log Machine-z", "almost_all_2d_histogram.pdf", 0)
    #import ipdb; ipdb.set_trace() # debugging code
    data = {'True Z': x, 'Predicted Z': yCorrected}
    df = pandas.DataFrame(data=data)
    df.to_csv("almost_all_2d_histogram.dat", sep=" ", index=False)

    zDiff = np.log10(np.abs((np.array(yCorrected) - np.array(x))/(np.array(x) + 0.01))) # 0.01 added to prevent infinity values
    #print zDiff
    #import ipdb; ipdb.set_trace() # debugging code
    histogram(zDiff, 15, 0, 0, 0, 0, '(Machine_z - Real_z)/Real_z Distribution', 'log ((Machine_z - Real_z)/Real_z)', 'Number of GRBs', "almost_all_histogram.pdf", y_log=0)

    return corr_val

def get_machine_z(request, predictors, response, ntree = 100, nodesize = 3, mtry = 4, random_seed = 999, weights=[]):
    num = len(predictors)
    num_repeat = num
    index = set(range(num))
    nsim = 100
    x = []
    y = []
    yerr = []

    """
    for i in range(num_repeat):
        print "Sim #: ", i
        #pick = set(np.random.random_integers(0, num-1, 1))
        pick = set([i])
        rest = index - pick
        #rest = random.sample(rest, num_sample)
        #print pick
        #print rest
        machine_z_arr = []
        for j in range(nsim):
            if len(weights) > 0:
                machinez = ml_engine(predictors[list(rest)], response[list(rest)], predictors[list(pick)],
                                ntree = ntree, nodesize = nodesize, mtry = mtry, random_seed = random_seed, weights=weights[list(rest)])
            else:
                machinez = ml_engine(predictors[list(rest)], response[list(rest)], predictors[list(pick)],
                                ntree = ntree, nodesize = nodesize, mtry = mtry, random_seed = random_seed)
            machine_z_arr.append(machinez)
        machine_z_arr = np.array(machine_z_arr)

        x.append(response[list(pick)][0])
        y.append(machine_z_arr.mean())
        yerr.append(machine_z_arr.std())

    #import ipdb; ipdb.set_trace() # debugging code

    x = np.array(x)
    y = np.array(y)
    yerr = np.array(yerr)
    fit, fitcov = optimization.curve_fit(func, x, y, sigma=yerr, absolute_sigma=False)
    fiterr = np.sqrt(np.diag(fitcov))
    #fiterr = np.diag(fitcov)
    c = fit[0]
    cerr = fiterr[0]
    m = fit[1]
    merr = fiterr[1]
    print 'm: ', m, ' merr: ', merr, '  c: ', c, '  cerr: ', cerr
    yCorrected = (y - c)/m
    yCorrectedErr2 = (yerr*yerr + cerr*cerr + yCorrected*yCorrected*merr*merr)/m/m
    yCorrectedErr = np.sqrt(yCorrectedErr2)

    corr_val = corr(x, y)
    statistics_str = "(Correlation Coefficient : {0:.3})".format(corr_val)
    #xyplot(x, y, 0, 10, 2.9, 3.02, "Redshift Predictor " + statistics_str, "Redshift", "Predicted Redshift", "almost_all_correlation.pdf", 0)
    #xyplot(x, y, 0, 10, min(y), max(y), "Redshift Predictor " + statistics_str, "Redshift", "Predicted Redshift", "almost_all_correlation.pdf", 0)
    xyploterr(x, y, yerr, 0, 10, 0, 10, "Redshift Predictor " + statistics_str, "Redshift", "Uncorrected Machine-z", "almost_all_correlation.pdf", 1)

    #import ipdb; ipdb.set_trace() # debugging code
    corr_val = corr(x, yCorrected)
    statistics_str = "(Correlation Coefficient : {0:.3})".format(corr_val)
    #xyplot(x, yCorrected, 0, 10, 0, 10, "Redshift Predictor " + statistics_str, "Redshift", "Predicted Redshift", "almost_all_correlation_corrected.pdf", 0)
    #xyplot(x, yCorrected, 0, 10, 0, 10, "Redshift Predictor (Corrected) " + statistics_str, "Redshift", "Predicted Redshift", "almost_all_correlation_corrected.pdf", 0)
    xyploterr(x, yCorrected, yCorrectedErr, 0, 10, -2, 10, "Redshift Predictor (Corrected) " + statistics_str, "Redshift", "Corrected Machine-z", "almost_all_correlation_corrected.pdf", 0)

    histogram_2d(x, yCorrected, 25, 0.0, 10.0, 0.0, 10.0, "Machine-z " + statistics_str, "log Redshift", "log Machine-z", "almost_all_2d_histogram.pdf", 0)
    #import ipdb; ipdb.set_trace() # debugging code
    data = {'True Z': x, 'Predicted Z': yCorrected}
    df = pandas.DataFrame(data=data)
    df.to_csv("almost_all_2d_histogram.dat", sep=" ", index=False)

    zDiff = np.log10(np.abs((np.array(yCorrected) - np.array(x))/(np.array(x) + 0.01))) # 0.01 added to prevent infinity values
    #print zDiff
    #import ipdb; ipdb.set_trace() # debugging code
    histogram(zDiff, 15, 0, 0, 0, 0, '(Machine_z - Real_z)/Real_z Distribution', 'log ((Machine_z - Real_z)/Real_z)', 'Number of GRBs', "almost_all_histogram.pdf", y_log=0)
    #"""

    machine_z_arr = []
    for j in range(nsim):
        #import ipdb; ipdb.set_trace() # debugging code
        machine_z = ml_engine(predictors, response, request,
                                ntree=ntree,
                                nodesize=nodesize,
                                mtry=mtry,
                                random_seed=random_seed)
        machine_z_arr.append(machine_z)

    machine_z_arr = np.array(machine_z_arr)
    machine_z = np.mean(machine_z_arr)
    machine_z_err = np.std(machine_z_arr)

    #import ipdb; ipdb.set_trace() # debugging code
    """
    m = 0.373843966474
    c = 0.90125780356
    merr = 0.0272578438485
    cerr = 0.0516998519467
    #"""

    m = 0.35
    c = 1.07
    merr = 0.03
    cerr = 0.05

    machine_z_corrected = (machine_z - c)/m
    machine_z_correctedErr2 = (machine_z_err*machine_z_err + cerr*cerr + machine_z_corrected*machine_z_corrected*merr*merr)/m/m
    machine_z_correctedErr = np.sqrt(machine_z_correctedErr2)

    return machine_z_corrected, machine_z_correctedErr

def read_train_file(filename, pfeatures):
    grb_catalog = pandas.read_csv(filename, dtype=np.float64)
    grb_catalog_headers = grb_catalog.columns
    feature_num = len(grb_catalog_headers) - 1
    print "Number of Features: ", feature_num
    #print grb_catalog_headers
    #for col in grb_catalog_headers:
    #    print col, ":", -1000
    #import ipdb; ipdb.set_trace() # debugging code
    response = np.array(grb_catalog[grb_catalog_headers[-1]])

    if len(pfeatures)==0:
        pick_features = range(len(grb_catalog_headers)-1)
    else:
        pick_features = pfeatures
    predictors = np.array(grb_catalog[grb_catalog_headers[pick_features]])
    #print grb_catalog_headers[pick_features]
    return predictors, response

def read_predic_file(filename, pfeatures):
    request = pandas.read_csv(filename, sep=":")
    headers = request.columns
    request = np.array(request[headers[1]], dtype=np.float64)

    if len(pfeatures)!=0:
        request = request[pfeatures]

    return request

def get_high_z_classification(request, predictors, response, z_theshold=4.0, ntree = 100, nodesize = 3, mtry = 4, random_seed = 999, weights=[]):

    response_c = np.array([1 if z > z_theshold else 0 for z in response])

    classifier = RandomForestClassifier(n_estimators=ntree,
                                        criterion='gini',
                                        #criterion='entropy',
                                        min_samples_leaf=nodesize,
                                        max_features=mtry,
                                        max_depth=3,
                                        #n_jobs = 6,
                                        random_state=random_seed)

    # Code to draw the ROC curve
    """
    plot_name = "roc_curve.pdf"
    X = predictors
    y = response_c
    n_sim = 100
    sim_mean_tpr = 0.0
    sim_mean_thr = 0.0
    for k in range(n_sim):
        print "Sim: ", k
        # Run classifier with cross-validation and plot ROC curves
        cv = StratifiedKFold(y, n_folds=10, shuffle=True) # perform 10 fold cross validation
        mean_tpr = 0.0
        mean_thr = 0.0
        mean_fpr = np.linspace(0, 1, 100)
        for i, (train, test) in enumerate(cv):
            #classifier.fit(X[train], y[train], sample_weight=weights[train])
            classifier.fit(X[train], y[train])
            probas_ = classifier.predict_proba(X[test])
            # Compute ROC curve and area the curve
            fpr, tpr, thresholds = roc_curve(y[test], probas_[:, 1])
            #print thresholds
            mean_tpr += interp(mean_fpr, fpr, tpr)
            mean_thr += interp(mean_fpr, fpr, thresholds)
            mean_tpr[0] = 0.0
        mean_tpr /= len(cv)
        mean_thr /= len(cv)
        mean_tpr[-1] = 1.0
        sim_mean_tpr += mean_tpr
        sim_mean_thr += mean_thr

    sim_mean_tpr /= n_sim
    sim_mean_thr /= n_sim

    mean_auc = auc(mean_fpr, sim_mean_tpr)
    plt.plot([0, 1], [0, 1], 'k--', label='Random')
    plt.plot(mean_fpr, sim_mean_tpr, 'b-',
             label='Mean ROC (Area = %0.2f)' % mean_auc, lw=2)

    plt.plot(mean_fpr, sim_mean_thr, 'r-',
             label='Threshold Probability', lw=2)

    #data_file_name = plot_name.split('.')[0] + ".dat"
    #data = {'mean_fpr': mean_fpr, 'sim_mean_tpr': sim_mean_tpr, 'mean_auc': mean_auc}
    #pickle.dump(data, open(data_file_name, "wb"))

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    #plt.xlabel('False Positive Rate (Num. Features = %i)' % num_features)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig(plot_name)
    plt.clf()
    #"""

    #import ipdb; ipdb.set_trace() # debugging code

    classifier.fit(predictors, response_c)
    probas = classifier.predict_proba(request)
    probability_of_high_z = probas[:,1]

    high_z_threshold = 0.1

    if probability_of_high_z > high_z_threshold:
        high_z = True
    else:
        high_z = False

    #import ipdb; ipdb.set_trace() # debugging code
    return high_z

def ml_engine_score(predictors, response, ntree = 100, nodesize = 3, mtry = 4, random_seed = 999, weights=[]):
    clf = RandomForestClassifier(n_estimators = ntree,
                                 criterion='gini',
                                 #criterion='entropy',
                                 min_samples_leaf = nodesize,
                                 max_features = mtry,
                                 max_depth=3,
                                 #n_jobs = 6,
                                 random_state = random_seed)
    #printe len(predictors), len(response), len(weights)
    if len(weights) > 0:
        clf.fit(predictors, response, sample_weight=weights)
    else:
        clf.fit(predictors, response)

    highz_probability_training = []
    prob = clf.predict_proba(predictors)
    for k in range(len(predictors)):
        #print clf.predict(predictors[k])[0], response[k], prob[k][1], clf.predict_proba(predictors[k])[0][1], prob[k][1]
        highz_probability_training.append(prob[k][1])
    highz_probability_training = np.array(highz_probability_training)

    return clf, highz_probability_training

def get_highz_score(request, predictors, response, z_theshold=4.0, ntree = 100, nodesize = 3, mtry = 4, random_seed = 999, weights=[]):
    response_c = np.array([1 if z > z_theshold else 0 for z in response])
    sample_weight = np.array([1 if z == 1 else 1 for z in response_c])
    clf, highz_probability_training = ml_engine_score(predictors, response_c,
                                                      ntree=ntree,
                                                      nodesize=nodesize,
                                                      mtry=mtry,
                                                      random_seed=None,
                                                      weights=sample_weight)

    N = float(len(highz_probability_training))
    prob = clf.predict_proba(request)
    highz_probability = prob[0][1]
    rank = rankdata(np.append(highz_probability, highz_probability_training)) # try to find the rank
    n = rank[0]
    #Q_hat = n/(N+1)
    #Q_hat = (N-n)/(N+1)
    Q_hat = (N-n+1)/(N+1)
    #print Q_hat
    #import ipdb; ipdb.set_trace() # debugging code
    return Q_hat

def get_highz_information(request):

    highz_results = []

    train_file = machine_z_data_file
    z_theshold = 4.0

    pick_features = [0, 10, 16, 24, 5, 18, 4, 12, 14, 20, 1] # selected features from the feature analysis: corr = 0.612

    predictors, response = read_train_file(train_file, pick_features)
    #import ipdb; ipdb.set_trace() # debugging code

    numtree = 100
    nodes = 1
    mtry_val = 5

    machine_z, machine_zErr = get_machine_z(request[pick_features], predictors, response,
                                            ntree=numtree,
                                            nodesize=nodes,
                                            mtry=mtry_val,
                                            random_seed=None,
                                            weights=[])

    #print "Machine z :", machine_z, " Machine z Err:", machine_zErr
    highz_results.append(machine_z)
    highz_results.append(machine_zErr)

    pick_features = [0, 14, 16, 24, 4, 20, 18, 22, 12, 10, 23, 9, 5, 6] # selected features from the feature analysis: ROC area = 0.89

    predictors, response = read_train_file(train_file, pick_features) # reload the traning set with new features
    #import ipdb; ipdb.set_trace() # debugging code

    numtree = 300
    nodes = 12
    mtry_val = len(pick_features)

    #import ipdb; ipdb.set_trace() # debugging code

    high_z = get_high_z_classification(request[pick_features], predictors, response,
                                       z_theshold=z_theshold,
                                       ntree=numtree,
                                       nodesize=nodes,
                                       mtry=mtry_val,
                                       random_seed=None,
                                       weights=[])

    #if high_z:
    #    print "This burst is high-z (z > 4)"
    #else:
    #    print "This burst is low-z (z < 4)"

    highz_results.append(high_z)

    #import ipdb; ipdb.set_trace() # debugging code

    q_score = get_highz_score([request[pick_features]], predictors, response, z_theshold=4.0, ntree=numtree, nodesize=nodes, mtry=mtry_val, random_seed=None, weights=[])

    #print "\nIf you have resources to follow-up only <{0:.1%} of the GRBs then observe this event.\n".format(q_score)

    highz_results.append(q_score*100.0)

    #import ipdb; ipdb.set_trace() # debugging code

    return highz_results

if __name__ == '__main__':

    get_highz_information()

