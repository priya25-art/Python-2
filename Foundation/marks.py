marks = int(input("Enter marks: "))

if marks >= 90:
    print("Grade: A")
    print("Excellent performance!")
elif marks >= 80:
    print("Grade: B")
    print("Very good performance!")
elif marks >= 70:
    print("Grade: C")
    print("Good performance!")
elif marks >= 60:
    print("Grade: D")
    print("Needs improvement.")
else:
    print("Grade: F")
    print("You need to work harder.")
def grade_system(details):
    print(details)


name = input("Enter your name: ")
age = int(input("Enter your age: "))
print("Execution completed successfully.")
grade_system(f"Name: {name}, Age: {age}, Marks: {marks}")