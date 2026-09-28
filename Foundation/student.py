def grade_system(marks):
    if marks >= 90:
        return "Grade:A - Excellent Performance"
    elif marks >= 80:
        return "Grade:B - Very Good Performance"
    elif marks >= 70:
        return "Grade:C - Good Performance"
    elif marks >= 60:
        return "Grade:D - Needs Improvement"
    else:
        return "Grade:F - You need to work harder"

class student_name:
    def __init__(self, name, total_marks):
        self.name = name
        self.total_marks = total_marks

    def get_details(self):
        return {
            "name": self.name,
            "total_marks": self.total_marks,
        }


student_names = []
for _ in range(5):
    student = student_name(
        input("Enter student name: "),
        int(input("Enter total marks: ")),
    )
    student_names.append(student)
    print([student.get_details() for student in student_names])
