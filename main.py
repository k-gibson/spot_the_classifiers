import random
import matplotlib.pyplot as plt
import numpy as np
import tree_utils
import utils
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

'''
Converts string values to usable numeric values
Parameter table: a single column table to be converted
Returns return_table: a table of converted values
'''


def convert_to_numeric(table):
    return_table = []
    index = 0
    for value in table:
        return_table.append(float(table[index]))
        index += 1
    return return_table


'''
Finds the coefficient for the linear regression of a scatterplot
Parameter xvalues: the table of values for the x axis
Parameter yvalues: the table of values of the y axis
Returns (b1,b2): the slope and y intercept of the linear regression
'''


def get_coefficient(xvalues, yvalues):
    size = np.size(xvalues)
    # find the mean of xvalues and yvalues
    xmean = np.mean(xvalues)
    ymean = np.mean(yvalues)
    # calculate the cross-deviation and deviation about x
    cross_deviation = np.sum(yvalues*xvalues) - size*ymean*xmean
    xdeviation = np.sum(xvalues*xvalues) - size*xmean*xmean
    # calculate the regression coefficients
    b2 = cross_deviation / xdeviation  # this is the slope (m)
    b1 = ymean - b2*xmean  # this is y intercept (b)
    return (b1, b2)


'''
Creates a scatter plot comparing two data tables
Parameter yaxis_column: single column table to be plotted on the y axis
Parameter xaxis_column: single column table to be plotted on the x axis
Parameter filename: the name of the file to save the graph to
Parameter titlename: the title for the graph
Parameter yaxis_label: the label for the y axis
Parameter step: the step of the program to plot
'''


def create_scatter_plot(xaxis_column, yaxis_column, filename, xlabel):
    plt.figure()
    xvalues = convert_to_numeric(xaxis_column)
    yvalues = convert_to_numeric(yaxis_column)
    plt.scatter(xvalues, yvalues, c="b")
    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel("Popularity")
    plt.title(xlabel + " vs Popularity")
    plt.savefig(filename)
    plt.close()


def main():
    '''audio_data = []
    utils.read_file_to_table("small_audio_data.csv", audio_data)
    print("done reading")
    headers = ["Acousticness", "Danceability", "Duration", "Energy", "Instrumentalness", "Key",
               "Liveness", "Loudness", "Mode", "Speechiness", "Tempo", "Time Signature", "Valence"]
    for i in range(0, 13):
        filename = headers[i] + ".pdf"
        create_scatter_plot(utils.get_column(audio_data, i), utils.get_column(
            audio_data, 13), filename, headers[i])'''

    # kNN classifier to predict popularity (index 13)
    # using: acousticness (0), danceability (1), duration (2), energy (3), instrumentalness (4),
    # liveness (6), loudness (7), speechiness (9), tempo (10), valence (12)
    trimmed_data = []
    utils.read_file_to_table("small_audio_data.csv", trimmed_data, [
                             0, 1, 2, 3, 4, 6, 7, 9, 10, 12, 13])

    # normalize duration (new index = 2), loudness (new index = 6), tempo (new index = 8)
    duration = utils.get_column(trimmed_data, 2)
    normalized_duration = utils.normalize(duration)
    loudness = utils.get_column(trimmed_data, 6)
    normalized_loudness = utils.normalize(loudness)
    tempo = utils.get_column(trimmed_data, 8)
    normalized_tempo = utils.normalize(tempo)

    # update table with normalized values
    # and discretize popularity
    for i in range(len(trimmed_data)):
        trimmed_data[i][2] = normalized_duration[i]
        trimmed_data[i][6] = normalized_loudness[i]
        trimmed_data[i][8] = normalized_tempo[i]
        trimmed_data[i][-1] = utils.discretize_popularity(trimmed_data[i][-1])

    # decision trees
    # values for this tree are already between 0 and 1
    col_names = ["acousticness", "danceability", "duration", "energy",
                 "instrumentalness", "liveness", "loudness", "speechiness", "tempo", "valence", "popularity"]
    labels = {"acousticness": "Acousticness", "danceability": "Danceability", "duration": "Duration", "energy": "Energy", "instrumentalness": "Instrumentalness",
              "liveness": "Liveness", "loudness": "Loudness", "speechiness": "Speechiness", "tempo": "Tempo", "valence": "Valence", "popularity": "Popularity"}
    att_domains = {0: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   1: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   2: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   3: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   4: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   5: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   6: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   7: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   8: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   9: [">=0.25", ">=0.50", ">=0.75", ">=1.0"],
                   10: [">=25", ">=50", ">=75", ">=100"]}
    class_index = len(col_names) - 1
    # att_indexes is a list of attributes to use for building the tree
    att_indexes = list(range(len(col_names) - 1))
    #spotify_tree = tree_utils.tdidt(tree_data, att_indexes, att_domains, class_index, col_names)
    #tree_utils.create_dot_tree(spotify_tree, labels, "spotify_tree")
    folds = utils.stratified_cross_folds(trimmed_data, 10)
    num_correct = 0
    for i in range(0, 10):  # range had to change
        train, test = utils.set_up_train_test(i, folds)
        actual_popularities = [x[-1] for x in test]
        att_indexes = list(range(len(col_names) - 1))
        predicted_popularities = tree_utils.tree_classifier(
            train, test, att_indexes, att_domains, class_index, col_names)
        for i in range(len(test)):
            if actual_popularities[i] == predicted_popularities[i]:
                num_correct += 1
    accuracy = num_correct / len(trimmed_data)
    print("Accuracy Decision Tree: " + str(round(accuracy * 100, 2)) + "%")

    # generate 10 stratified cross folds
    folds = utils.stratified_cross_folds(trimmed_data, 10)
    num_correct = 0
    for i in range(0, 10):
        train, test = utils.set_up_train_test(i, folds)
        actual_popularities = [x[-1] for x in test]
        predicted_popularities = utils.knn_classifier(train, test)
        for i in range(len(test)):
            if actual_popularities[i] == predicted_popularities[i]:
                num_correct += 1
        print(num_correct)
    accuracy = num_correct / len(trimmed_data)
    print("Accuracy kNN: " + str(round(accuracy * 100, 2)) + "%")

    # naive bayes
    num_correct_bayes = 0
    for i in range(0, 10):
        train, test = utils.set_up_train_test(i, folds)
        priors = utils.compute_probabilities(train)
        actual_popularities_bayes = [x[-1] for x in test]
        predicted_popularities_bayes = []
        for instance in test:
            predicted_popularity_bayes = utils.naive_bayes_classifier(
                priors, instance, train)
            predicted_popularities_bayes.append(predicted_popularity_bayes)
        for i in range(len(test)):
            if actual_popularities_bayes[i] == predicted_popularities_bayes[i]:
                num_correct_bayes += 1
        print(num_correct_bayes)
    accuracy_bayes = num_correct_bayes / len(trimmed_data)
    print("Accuracy Naive Bayes: " + str(round(accuracy_bayes * 100, 2)) + "%")

    # ensemble classifier (kNN)
    # generate five weak learners, each using a different subset of attributes
    num_correct_ensemble = 0
    for i in range(10):
        train, test = utils.set_up_train_test(i, folds)
        actual_popularities = [x[-1] for x in test]
        predicted_popularities = []
        for instance in test:
            predictions = []
            for j in range(6):
                training_subset = train[j:j+4]
                prediction = utils.compute_class_knn(instance, training_subset)
                predictions.append(prediction)
            # use simple majority voting
            np_arr = np.array(predictions)
            majority_vote = np.bincount(np_arr).argmax()
            predicted_popularities.append(majority_vote)
        for i in range(len(test)):
            if predicted_popularities[i] == actual_popularities[i]:
                num_correct_ensemble += 1
    accuracy_ensemble = num_correct_ensemble / len(trimmed_data)
    print("Accuracy ensemble kNN: " +
          str(round(accuracy_ensemble * 100, 2)) + "%")

    # compare with scikit-learn kNN
    df = pd.DataFrame(trimmed_data)
    X = np.array(df.loc[:, 0:9])  # features
    y = np.array(df.loc[:, 10])  # class label (popularity)

    # split into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

    knn = KNeighborsClassifier(n_neighbors=8)
    knn.fit(X_train, y_train)
    prediction = knn.predict(X_test)
    print("Scikit-learn accuracy (kNN): " +
          str(round(accuracy_score(y_test, prediction) * 100, 2)) + "%")


if __name__ == "__main__":
    main()
