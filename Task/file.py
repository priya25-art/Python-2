ct = 3
while ct >= 0:
    std = input("Enter your name: ")
    ct -= 1
    with open(r"C:\Priyadharshini K\Python\Task\std_details.txt", "a", encoding="utf-8") as file:
        file.write(std + "\n")

# Alternative way: define path separately
path = r"C:\Priyadharshini K\Python\Task\std_details.txt"
with open(path, "r", encoding="utf-8") as file:
    content = file.read()
print(content)


