student = {
    "Name": "Alice",
    "Age": 20,
    "Grade": "A5",
    "Email": "alice@yahoo.com",
    "City": "New York"
}

# Print all details
print(student)
print(student["Name"])
print(student["Age"])
print(student["Grade"])
print(student["Email"])
print(student["City"])

# Delete specific keys
del student["Email"]          # removes Email
age = student.pop("Age")      # removes Age and stores it in variable 'age'

# Print dictionary after deletions
print(student)

# Finally delete the entire dictionary
del student

# ⚠️ Important: Do NOT try to print(student) after this point,
# because the dictionary no longer exists and will raise NameError.
