import pandas as pd
import glob

# Initialize an empty list to store DataFrames
dataframes = []

# Use glob to match all files with the same pattern
file_pattern = "aapl_30x_2023*.txt"  # Adjust pattern to match your filenames
for file in glob.glob(file_pattern):
    # Load each file
    df = pd.read_csv(file, delimiter=", ", engine='python')

    # Convert the date columns to datetime
    # df["[QUOTE_DATE]"] = pd.to_datetime(df["[QUOTE_DATE]"])
    # df["[EXPIRE_DATE]"] = pd.to_datetime(df["[EXPIRE_DATE]"])

    # Drop unnecessary columns
    # df = df.drop(df.columns[[0, 6, 8,9,10,11,12, 13,14, 16,17,18, 20,21,22, 24,25,26,27,28, 29,30]], axis=1)

    # Append the processed DataFrame to the list
    dataframes.append(df)

# Concatenate all DataFrames into one
mega_df = pd.concat(dataframes, ignore_index=True)

# Save the combined DataFrame to a new file if needed
mega_df.to_csv("aapl_30x_2023_full_test.csv", index=False)

# Print a sample of the combined data
print(mega_df.head())
