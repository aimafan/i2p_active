import pandas as pd
from io import StringIO


filename = "../../../data/output.csv"

with open(filename, "r") as file:
    csv_data = file.read()

# Convert the CSV data to a DataFrame
df = pd.read_csv(StringIO(csv_data))

# Count the number of occurrences for each result value
result_counts = df['result'].value_counts().sort_index()


print(result_counts)