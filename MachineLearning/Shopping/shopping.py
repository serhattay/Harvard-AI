import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    month_to_number = {
        "Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3,
        "May": 4, "June": 5, "Jul": 6, "Aug": 7,
        "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11
    }

    int_list = ["Administrative", "Informational", "ProductRelated",
                "OperatingSystems", "Browser", "Region", "TrafficType"]
    float_list = ["Administrative_Duration", "Informational_Duration",
                  "ProductRelated_Duration", "BounceRates", "ExitRates",
                  "PageValues", "SpecialDay"]

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)

        evidence = []
        labels = []

        for row in reader:
            sub_evidence = []
            for key, value in row.items():
                if key == "Revenue":
                    labels.append(value)
                elif key in int_list:
                    sub_evidence.append(int(value))
                elif key in float_list:
                    sub_evidence.append(float(value))
                elif key == "Month":
                    sub_evidence.append(month_to_number[value])
                elif key == "VisitorType":
                    sub_evidence.append(1 if value == "Returning_Visitor" else 0)
                elif key == "Weekend":
                    sub_evidence.append(1 if value == "TRUE" else "FALSE")

            evidence.append(sub_evidence)

    return evidence, labels

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)

    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    number_of_correct_positives = 0
    # Computer guessed negative but it was positive
    number_of_incorrect_positives = 0
    number_of_correct_negatives = 0
    number_of_incorrect_negatives = 0

    for prediction, label in zip(predictions, labels):
        if label == prediction:
            if prediction == 1:
                number_of_correct_positives += 1
            elif prediction == 0:
                number_of_correct_negatives += 1
        elif label != prediction:
            if label == 1:
                number_of_incorrect_positives += 1
            elif label == 0:
                number_of_incorrect_negatives += 1

    sensitivity = number_of_correct_positives / (number_of_correct_positives + number_of_incorrect_positives)
    specificity = number_of_correct_negatives / (number_of_correct_negatives + number_of_incorrect_negatives)

    return sensitivity, specificity


if __name__ == "__main__":
    main()
