from flask import Flask, render_template, request, redirect, flash
import pandas as pd
from sklearn.cluster import MeanShift
import numpy as np
import json

app = Flask(__name__)
app.secret_key = 'secret_key'

# Route for the main page


@app.route("/")
def index():
    return render_template("./index.html")

# Route for clustering


@app.route("/cluster", methods=["POST"])
def cluster():
    parameter = request.form.get("parameter")

    # Validate the selected parameter
    valid_parameters = ["Usia", "Pendapatan", "Pengeluaran"]
    if parameter not in valid_parameters:
        flash("The selected parameter is invalid.", "error")
        return redirect("/")

    try:
        # Read the dataset from the CSV file
        df = pd.read_csv("Pengunjung_Mall.csv")

        # Extract the column corresponding to the selected parameter
        if parameter == "Usia":
            data = np.array(df["Usia"])
        elif parameter == "Pendapatan":
            data = np.array(df["Pendapatan_Tahunan_Ribuan_USD"])
        else:
            data = np.array(df["Pengeluaran_USD"])

        # Perform clustering using MeanShift algorithm
        clustering = MeanShift().fit(data.reshape(-1, 1))

        # Get the labels from the clustering result
        labels = clustering.labels_

        # Combine similar groups into one group
        unique_labels = np.unique(labels)
        combined_labels = []

        for label in labels:
            if label in unique_labels:
                combined_labels.append(str(df.loc[label, "ID_Pelanggan"]))
                unique_labels = np.delete(unique_labels, 0)
            else:
                combined_labels.append(str(df.loc[label, "ID_Pelanggan"]))

        # Convert the labels to a single string without commas and spaces
        combined_labels_string = ''.join(combined_labels)

        return render_template("result.html", labels=combined_labels_string)

    except Exception as e:
        flash("An error occurred while performing clustering: " + str(e), "error")
        return redirect("/")

# Route to reset the page


@app.route("/reset")
def reset():
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
