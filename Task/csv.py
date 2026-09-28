from _csv import reader as csv_reader, writer as csv_writer

with open(r"C:\Priyadharshini K\Python\Task\data.csv", newline="") as file:
    rows = csv_reader(file)
    headers = next(rows)
    for values in rows:
        row = dict(zip(headers, values))
        print(row)
with open(r"C:\Priyadharshini K\Python\Task\data.csv", "a", newline="") as file:
    writer = csv_writer(file)
    writer.writerow(["Mithra","ECE",
                     "Sujitha","CS", 
                     "Janani","CS"])
