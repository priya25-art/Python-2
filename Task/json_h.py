import json

# to load and display data
with open(r"C:\Priyadharshini K\Python\Task\std.data.json", "r") as j_file:
    student=json.load(j_file)
    print(student["marks"]["Power BI"])
    student = json.dumps(student,indent=2)
# Define the student dictionary
student = {}

# Add courses key with a list value
student["courses"] = ["Python"]

print(student)
