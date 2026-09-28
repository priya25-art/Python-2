class Student:
    def __init__(self, name, student_id, dept, marks, attendance=0):
        university = "Nova University"
        self.name = name
        self.student_id = student_id
        self.dept = dept
        self.marks = marks
        self.attendance = 0
        def display(self):
            print(self)
            

    def __str__(self):
        return f"Student(Name: {self.name}, ID: {self.student_id}, Dept: {self.dept}, Marks: {self.marks}, Attendance: {self.attendance})"

# Creating student objects
std1 = Student("Arun", "CS101", "CSE", [89, 90, 78])
std2 = Student("Varun", "IT101", "IT", [89, 90, 100])
std3 = Student("Alice", "BBA101","BBA",[88,99,100])
std4 = Student("John","BCA101","BCA",[70,90,99])
std5 = Student("David","BA101","BA",[80,97,96])
# Printing type and details
print(type(std1))       # Shows the class type
print(std1)             # Shows readable details
print(std2)
print(std3)
print(std4)
print(std5)

print(std1.marks)
std1_marks =[89,90,91]
print(std2.marks)
std2_marks=[98,97,96]
print(std3.marks)
std3_marks=[96,94,93]
print(std4.marks)
std4_marks=[89,87,83]
print(std5.marks)
std5_marks=[80,76,75]
def return_average(*mark_lists):
    """Return the average mark across all provided students."""
    marks = [mark for student_marks in mark_lists for mark in student_marks]
    return sum(marks) / len(marks) if marks else 0


print(return_average(std1_marks, std2_marks, std3_marks, std4_marks, std5_marks))

class Student:
    def __init__(self, name):
        self.name = name
        self.__marks = []   # private attribute (encapsulation)

    def add_marks(self, mark):
        # method to add marks internally
        self.__marks.append(mark)

    def calculate_cgpa(self):
        # private data is used internally, not exposed
        if len(self.__marks) == 0:
            return 0
        # CGPA formula: average marks / 10 (assuming marks out of 100)
        return sum(self.__marks) / len(self.__marks) / 10

    def display_cgpa(self):
        print(f"Student: {self.name}")
        print(f"CGPA: {self.calculate_cgpa():.2f}")


# Example usage
student1 = Student("Alice")
student1.add_marks(85)
student1.add_marks(90)
student1.add_marks(78)
student1.add_marks(88)
student2 = Student("Bob")
student2.add_marks(89)
# Only CGPA is displayed, marks remain hidden
student1.display_cgpa()
