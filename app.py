from flask import Flask, render_template, request, redirect, flash
import pandas as pd
import numpy as np
from sklearn.cluster import MeanShift

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

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

        # Extract the columns corresponding to the selected parameter and gender
        if parameter == "Usia":
            data = np.array(df[["Usia", "Pendapatan_Tahunan_Ribuan_USD", "Pengeluaran_USD", "Gender"]])
        elif parameter == "Pendapatan":
            data = np.array(df[["Pendapatan_Tahunan_Ribuan_USD", "Usia", "Pengeluaran_USD", "Gender"]])
        else:
            data = np.array(df[["Pengeluaran_USD", "Usia", "Pendapatan_Tahunan_Ribuan_USD", "Gender"]])

        # Encode the gender feature as numeric values
        gender_mapping = {"Pria": 0, "Wanita": 1}
        data[:, 3] = [gender_mapping[gender] for gender in data[:, 3]]

        np.random.seed(42)

        # Perform clustering using MeanShift algorithm
        clustering = MeanShift().fit(data)

        # Get the labels from the clustering result
        labels = clustering.labels_

        # Calculate the central point (centroid) of each cluster
        central_points = clustering.cluster_centers_[:, :-1]

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

        return render_template("result.html", labels=combined_labels_string, central_points=central_points)

    except Exception as e:
        flash("An error occurred while performing clustering: " + str(e), "error")
        return redirect("/")

@app.route("/reset")
def reset():
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
