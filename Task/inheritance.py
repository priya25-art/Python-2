import abc


class Person(abc.ABC):
    def __init__(self, name, email):
        self.name = name
        self.email = email

    @abc.abstractmethod
    def display_role(self):
        pass


class Student(Person):
    def __init__(self, name, email, dept):
        super().__init__(name, email)
        self.dept = dept

    def display_role(self):
        return "Student"


class Teacher(Student):
    def __init__(self, name, email, dept, empid, subjectshandled):
        super().__init__(name, email, dept)
        self.empid = empid
        self.subjectshandled = subjectshandled

    def display_role(self):
        return "Teacher"

class Animal:
    def sound(self):
        return "Any sound"


class Dog(Animal):
    def sound(self):
        return "Bark"


class Bird(Animal):
    def sound(self):
        return "Sing"


# Example usage
animals = [Animal(), Dog(), Bird()]

for a in animals:
    print(f"{a.__class__.__name__} makes sound: {a.sound()}")


std1 = Student("ABC","abc@gmail.com","cse")
print(std1.display_role())

# ✅ Creating objects
people = [
    Student("John", "john@gmail.com", "AI"),
    Teacher("David", "david@gmail.com", "CS", "E001", ["Python", "SQL"])
]

# Example usage
for person in people:
    print(person.name, "-", person.email)
    if isinstance(person, Teacher):
        print("Role:", person.display_role())
class HOD(Person):
    def __init__(self, name, email):
        super().__init__(name, email)

    def display_role(self):
        return "HOD"


