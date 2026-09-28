"""
Nova University - Student Management & Academic Service System
================================================================
Console application for the "Python Data Structures - Real-Time Application" brief.

DATA STRUCTURE DECISIONS (driven by the business requirement, not by what was taught last)

  Requirement                  Structure                 Why
  ---------------------------  ------------------------  ---------------------------------------------
  One student record           dict                      Named fields of mixed types (id, name, year ...)
  Multiple students            dict {ID: record}         Search by ID is a direct lookup, not a loop
  Unique Student IDs           dict keys (+ `in` check)  Keys can never repeat; membership test is O(1)
  Departments (master list)    dict {code: full name}    Needs code -> name relationship, unique codes
  Departments in use           set                       Only "is it present?" matters; no duplicates
  Courses of one student       set                       No duplicates allowed, order irrelevant
  Subject marks                dict {subject: mark}      Subject -> mark is a key/value relationship
  Subject order / grade bands  tuple                     Fixed, ordered, never modified
  Course participation groups  set of Student IDs        Union / intersection / difference operations
  Batch results / rows         list                      Ordered, may repeat, built for looping/sorting

Assumptions where the brief is silent (change the constants below if needed):
  * Pass mark is 50 per subject (the grade table makes "below 50" an F).l
  * A student PASSES only if every subject is >= PASS_MARK.
  * Grade is decided from the AVERAGE mark using the grade table.
  * Department codes are matched exactly (case-sensitive), as the brief asks.
  * A withdrawn student is deactivated, not deleted: the record is kept for audit,
    the ID stays reserved, and the student is skipped by all active processing.
"""

# ----------------------------------------------------------------------------
# CONSTANTS - business rules live in one place so they are easy to change
# ----------------------------------------------------------------------------
DEPARTMENTS = {
    "CSE": "Computer Science & Engineering",
    "IT": "Information Technology",
    "AI&DS": "Artificial Intelligence & Data Science",
    "ECE": "Electronics & Communication Engineering",
    "BBA": "Business Administration",
}
SUBJECTS = ("Python", "SQL", "Excel", "Power BI")
PASS_MARK = 50
MIN_ATTENDANCE = 75
MAX_YEAR = 4
GRADE_BANDS = ((90, "A"), (80, "B"), (70, "C"), (60, "D"), (50, "E"))
LOWEST_GRADE = "F"
ACTIVE = "Active"
WITHDRAWN = "Withdrawn"


# ----------------------------------------------------------------------------
# INPUT HELPERS - keep all validation loops out of the business logic
# ----------------------------------------------------------------------------
def read_text(prompt):
    """Read a non-empty string."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  [!] Input cannot be empty. Please try again.")


def read_valid(prompt, is_valid, error_message):
    """Keep asking until is_valid(value) is True; return the stripped value."""
    while True:
        value = input(prompt).strip()
        if is_valid(value):
            return value
        print(f"  [!] {error_message}")


def read_number(prompt, low, high, as_int=False):
    """Read a number between low and high (inclusive)."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw) if as_int else float(raw)
        except ValueError:
            print("  [!] Please enter a valid number.")
            continue
        if low <= value <= high:
            return value
        print(f"  [!] Value must be between {low} and {high}.")


def confirm(prompt):
    """Ask a yes/no question."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  [!] Please answer y or n.")


# ----------------------------------------------------------------------------
# VALIDATORS - small, reusable, return True/False
# ----------------------------------------------------------------------------
def is_valid_student_id(text):
    return text.isalnum()


def is_valid_name(text):
    cleaned = text.replace(" ", "").replace(".", "").replace("-", "")
    return cleaned.isalpha()


def is_valid_department(code):
    return code in DEPARTMENTS  # exact, case-sensitive match


def is_valid_email(text):
    if text.count("@") != 1 or " " in text:
        return False
    local, domain = text.split("@")
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


def is_valid_phone(text):
    return text.isdigit() and len(text) == 10


# ----------------------------------------------------------------------------
# STUDENT DATA LAYER - pure functions (no input/print) so they are easy to test
# ----------------------------------------------------------------------------
def create_student(student_id, name, department, year, email, phone):
    """Build one student record."""
    return {
        "id": student_id,
        "name": name,
        "department": department,
        "year": year,
        "email": email,
        "phone": phone,
        "attendance": None,   # percentage, None until recorded
        "marks": {},          # {subject: mark}
        "courses": set(),     # unique course names
        "status": ACTIVE,     # ACTIVE or WITHDRAWN
    }


def register_student(students, record):
    """Store the record unless the ID already exists. Returns True/False."""
    if record["id"] in students:
        return False
    students[record["id"]] = record
    return True


def active_students(students):
    """Active records only, sorted by ID. Withdrawn students never appear here."""
    return [students[sid] for sid in sorted(students) if students[sid]["status"] == ACTIVE]


# ----------------------------------------------------------------------------
# ACADEMIC CALCULATIONS
# ----------------------------------------------------------------------------
def calculate_total(marks):
    return sum(marks.values())


def calculate_average(marks):
    return sum(marks.values()) / len(marks) if marks else 0.0


def highest_mark(marks):
    subject = max(marks, key=marks.get)
    return subject, marks[subject]


def failed_subjects(marks):
    return [subject for subject in SUBJECTS if subject in marks and marks[subject] < PASS_MARK]


def determine_grade(average):
    for minimum, grade in GRADE_BANDS:
        if average >= minimum:
            return grade
    return LOWEST_GRADE


def is_eligible(attendance):
    """Attendance of exactly MIN_ATTENDANCE qualifies. None (not recorded) does not."""
    return attendance is not None and attendance >= MIN_ATTENDANCE


def has_complete_marks(student):
    return all(subject in student["marks"] for subject in SUBJECTS)


def build_result(student):
    """Full examination result, or None if marks are incomplete."""
    if not has_complete_marks(student):
        return None
    marks = student["marks"]
    average = calculate_average(marks)
    failed = failed_subjects(marks)
    return {
        "total": calculate_total(marks),
        "average": average,
        "highest": highest_mark(marks),
        "failed": failed,
        "result": "Fail" if failed else "Pass",
        "grade": determine_grade(average),
        "eligible": is_eligible(student["attendance"]),
    }


# ----------------------------------------------------------------------------
# COURSE HELPERS
# ----------------------------------------------------------------------------
def find_course(student, course):
    """Return the stored spelling of a course (case-insensitive), or None."""
    for existing in student["courses"]:
        if existing.casefold() == course.casefold():
            return existing
    return None


def add_course(student, course):
    if find_course(student, course) is not None:
        return False
    student["courses"].add(course)
    return True


def remove_course(student, course):
    """Remove the course; returns the stored spelling, or None if not registered."""
    existing = find_course(student, course)
    if existing is not None:
        student["courses"].remove(existing)
    return existing


def students_in_course(students, course):
    """Set of IDs of ACTIVE students registered for the course."""
    group = set()
    for student in active_students(students):
        if find_course(student, course) is not None:
            group.add(student["id"])
    return group


def find_duplicates(items):
    """Return the set of values that appear more than once in a list."""
    seen, duplicates = set(), set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return duplicates


def overlap_analysis(group_a, group_b):
    """Compare two groups of Student IDs using set operations."""
    a, b = set(group_a), set(group_b)
    return {
        "both": a & b,
        "only_a": a - b,
        "only_b": b - a,
        "either": a | b,
        "exactly_one": a ^ b,
        "duplicates_a": find_duplicates(group_a),
        "duplicates_b": find_duplicates(group_b),
        "completely_different": a.isdisjoint(b),
    }


# ----------------------------------------------------------------------------
# STATISTICS
# ----------------------------------------------------------------------------
def compute_statistics(students):
    active = active_students(students)
    per_department = {}
    scored = []  # (average, id, name) tuples
    eligible = 0
    failed = 0
    for student in active:
        dept = student["department"]
        per_department[dept] = per_department.get(dept, 0) + 1
        if is_eligible(student["attendance"]):
            eligible += 1
        result = build_result(student)
        if result is not None:
            scored.append((result["average"], student["id"], student["name"]))
            if result["result"] == "Fail":
                failed += 1
    stats = {
        "total": len(active),
        "per_department": per_department,
        "departments": {student["department"] for student in active},
        "eligible": eligible,
        "failed": failed,
        "pending": len(active) - len(scored),
        "highest": max(scored) if scored else None,
        "lowest": min(scored) if scored else None,
        "batch_average": sum(item[0] for item in scored) / len(scored) if scored else None,
    }
    return stats


# ----------------------------------------------------------------------------
# DISPLAY HELPERS
# ----------------------------------------------------------------------------
def fmt_mark(value):
    return "Not recorded" if value is None else f"{value:g}"


def fmt_attendance(value):
    return "Not recorded" if value is None else f"{value:g}%"


def eligibility_text(attendance):
    if attendance is None:
        return "Unknown"
    return "Eligible" if is_eligible(attendance) else "Not eligible"


def show_ids(label, ids):
    print(f"  {label}: {', '.join(sorted(ids)) or 'None'}")


def display_student(student):
    dept = student["department"]
    print(f"\n  Student ID  : {student['id']}")
    print(f"  Name        : {student['name']}")
    print(f"  Department  : {dept} - {DEPARTMENTS[dept]}")
    print(f"  Year        : {student['year']}")
    print(f"  Email       : {student['email']}")
    print(f"  Phone       : {student['phone']}")
    print(f"  Attendance  : {fmt_attendance(student['attendance'])}")
    marks_text = ", ".join(f"{s}: {fmt_mark(student['marks'].get(s))}" for s in SUBJECTS)
    print(f"  Marks       : {marks_text}")
    print(f"  Courses     : {', '.join(sorted(student['courses'])) or 'None'}")
    print(f"  Status      : {student['status']}")


def display_academic_summary(student):
    print(f"\nAcademic summary - {student['name']} ({student['id']})")
    for subject in SUBJECTS:
        print(f"  {subject:<10}: {fmt_mark(student['marks'].get(subject))}")
    result = build_result(student)
    if result is None:
        missing = [s for s in SUBJECTS if s not in student["marks"]]
        print("  Summary pending - marks missing for: " + ", ".join(missing))
        return None
    subject, mark = result["highest"]
    print(f"  Total          : {result['total']:g} / {100 * len(SUBJECTS)}")
    print(f"  Average        : {result['average']:.2f}")
    print(f"  Highest mark   : {subject} ({mark:g})")
    print(f"  Failed subjects: {', '.join(result['failed']) or 'None'}")
    return result


def display_result(student):
    result = display_academic_summary(student)
    print(f"  Attendance     : {fmt_attendance(student['attendance'])} -> {eligibility_text(student['attendance'])}")
    if result is None:
        print("  Result         : Pending (needs marks for every subject)")
        return
    print(f"  Result         : {result['result']}")
    print(f"  Grade          : {result['grade']}")


def display_all_students(students):
    if not students:
        print("  [!] No students registered yet.")
        return
    print(f"\n{'ID':<8}{'Name':<22}{'Dept':<8}{'Year':<6}{'Attendance':<14}{'Status'}")
    print("-" * 68)
    for sid in sorted(students):
        s = students[sid]
        print(f"{s['id']:<8}{s['name']:<22}{s['department']:<8}{s['year']:<6}"
              f"{fmt_attendance(s['attendance']):<14}{s['status']}")


def display_departments():
    print("\nAvailable departments:")
    for code, name in DEPARTMENTS.items():
        print(f"  {code:<6}- {name}")


def report_overlap(name_a, name_b, group_a, group_b):
    r = overlap_analysis(group_a, group_b)
    print(f"\nCourse overlap: {name_a} vs {name_b}")
    show_ids("Registered for BOTH", r["both"])
    show_ids(f"{name_a} but NOT {name_b}", r["only_a"])
    show_ids(f"{name_b} but NOT {name_a}", r["only_b"])
    show_ids("At least one of the two", r["either"])
    show_ids("Exactly one of the two", r["exactly_one"])
    show_ids(f"Duplicate IDs in {name_a} data", r["duplicates_a"])
    show_ids(f"Duplicate IDs in {name_b} data", r["duplicates_b"])
    print(f"  Groups completely different: {'Yes' if r['completely_different'] else 'No'}")


# ----------------------------------------------------------------------------
# PROMPT HELPERS - reused by registration AND update
# ----------------------------------------------------------------------------
def prompt_name():
    return read_valid("Student name: ", is_valid_name,
                      "Name must contain letters only (spaces, '.' and '-' allowed).")


def prompt_department():
    display_departments()
    codes = ", ".join(DEPARTMENTS)
    return read_valid("Department code: ", is_valid_department,
                      f"Invalid department. Enter exactly one of: {codes} (case-sensitive).")


def prompt_year():
    return read_number(f"Year (1-{MAX_YEAR}): ", 1, MAX_YEAR, as_int=True)


def prompt_email():
    return read_valid("Email: ", is_valid_email, "Enter a valid email, e.g. name@nova.edu")


def prompt_phone():
    return read_valid("Phone (10 digits): ", is_valid_phone, "Phone must be exactly 10 digits.")


def read_course(prompt):
    return " ".join(read_text(prompt).split())


def choose_subject():
    for number, subject in enumerate(SUBJECTS, start=1):
        print(f"  {number}. {subject}")
    index = read_number("Select subject number: ", 1, len(SUBJECTS), as_int=True)
    return SUBJECTS[index - 1]


def ask_for_student(students, active_only=True):
    """Ask for an ID and return the record, or None (after explaining why)."""
    if not students:
        print("  [!] No students registered yet.")
        return None
    student_id = input("Enter Student ID: ").strip().upper()
    student = students.get(student_id)
    if student is None:
        print(f"  [!] No student found with ID '{student_id}'.")
        return None
    if active_only and student["status"] != ACTIVE:
        print(f"  [!] {student_id} has withdrawn and is excluded from active processing.")
        return None
    return student


# ----------------------------------------------------------------------------
# MENU HANDLERS - each one does ONE job and delegates the logic to the layers above
# ----------------------------------------------------------------------------
def run_submenu(title, options, students):
    """Generic sub-menu loop. options = {key: (label, handler)}."""
    while True:
        print(f"\n=== {title} ===")
        for key, (label, _handler) in options.items():
            print(f"  {key}. {label}")
        print("  0. Back to main menu")
        choice = input("Select an option: ").strip()
        if choice == "0":
            return
        if choice in options:
            options[choice][1](students)
        else:
            print("  [!] Invalid selection. Please choose a number from the menu.")


# --- Student registration ---------------------------------------------------
def add_one_student(students):
    print("\n--- New Student Registration ---")
    student_id = read_valid("Student ID (e.g. ST101): ", is_valid_student_id,
                            "ID must contain letters/digits only, no spaces.").upper()
    if student_id in students:
        print(f"  [!] Student ID {student_id} already exists. Registration rejected.")
        return
    record = create_student(student_id, prompt_name(), prompt_department(),
                            prompt_year(), prompt_email(), prompt_phone())
    register_student(students, record)
    print(f"  [OK] {record['name']} registered with ID {student_id}.")


def menu_add_students(students):
    while True:
        add_one_student(students)
        if not confirm("Register another student? (y/n): "):
            break


def menu_update_student(students):
    student = ask_for_student(students)
    if student is None:
        return
    display_student(student)
    print("\nWhat would you like to update?")
    print("  1. Name  2. Department  3. Year  4. Email  5. Phone")
    choice = read_number("Select field: ", 1, 5, as_int=True)
    if choice == 1:
        student["name"] = prompt_name()
    elif choice == 2:
        student["department"] = prompt_department()
    elif choice == 3:
        student["year"] = prompt_year()
    elif choice == 4:
        student["email"] = prompt_email()
    else:
        student["phone"] = prompt_phone()
    print("  [OK] Student information updated.")


def menu_display_all(students):
    display_all_students(students)


def menu_registration(students):
    run_submenu("Student Registration", {
        "1": ("Register new student(s)", menu_add_students),
        "2": ("Update student information", menu_update_student),
        "3": ("Display all students", menu_display_all),
    }, students)


# --- Student search ---------------------------------------------------------
def menu_search(students):
    student = ask_for_student(students, active_only=False)
    if student is not None:
        display_student(student)


# --- Course registration ----------------------------------------------------
def menu_add_course(students):
    student = ask_for_student(students)
    if student is None:
        return
    course = read_course("Course to register: ")
    if add_course(student, course):
        print(f"  [OK] {student['name']} registered for {course}.")
    else:
        print(f"  [!] {student['name']} is already registered for {course}. Duplicate blocked.")


def menu_show_courses(students):
    student = ask_for_student(students)
    if student is None:
        return
    if not student["courses"]:
        print(f"  {student['name']} has no registered courses.")
        return
    print(f"\nCourses for {student['name']}:")
    for number, course in enumerate(sorted(student["courses"]), start=1):
        print(f"  {number}. {course}")


def menu_remove_course(students):
    student = ask_for_student(students)
    if student is None:
        return
    if not student["courses"]:
        print(f"  {student['name']} has no registered courses to withdraw from.")
        return
    print(f"Registered: {', '.join(sorted(student['courses']))}")
    course = read_course("Course to withdraw from: ")
    removed = remove_course(student, course)
    if removed is not None:
        print(f"  [OK] {student['name']} withdrawn from {removed}.")
    else:
        print(f"  [!] {student['name']} is not registered for {course}.")


def menu_overlap_live(students):
    course_a = read_course("First course: ")
    course_b = read_course("Second course: ")
    group_a = students_in_course(students, course_a)
    group_b = students_in_course(students, course_b)
    if not group_a and not group_b:
        print("  [!] No active students are registered for either course.")
        return
    report_overlap(course_a, course_b, group_a, group_b)


def menu_overlap_sample(_students):
    """Runs the exact example from the brief on raw lists (duplicates possible)."""
    python_training = ["ST101", "ST102", "ST103", "ST105"]
    sql_training = ["ST102", "ST103", "ST104", "ST106"]
    report_overlap("Python Training", "SQL Training", python_training, sql_training)


def menu_courses(students):
    run_submenu("Course Registration", {
        "1": ("Add a course for a student", menu_add_course),
        "2": ("Display a student's courses", menu_show_courses),
        "3": ("Withdraw a student from a course", menu_remove_course),
        "4": ("Course overlap analysis (live data)", menu_overlap_live),
        "5": ("Course overlap analysis (sample data from brief)", menu_overlap_sample),
    }, students)


# --- Attendance -------------------------------------------------------------
def menu_set_attendance(students):
    student = ask_for_student(students)
    if student is None:
        return
    student["attendance"] = read_number("Attendance % (0-100): ", 0, 100)
    print(f"  [OK] Attendance for {student['name']} set to {student['attendance']:g}% "
          f"-> {eligibility_text(student['attendance'])}.")


def menu_view_attendance(students):
    student = ask_for_student(students)
    if student is None:
        return
    print(f"  {student['name']}: {fmt_attendance(student['attendance'])} "
          f"-> {eligibility_text(student['attendance'])}")


def menu_below_attendance(students):
    active = active_students(students)
    if not active:
        print("  [!] No active students registered yet.")
        return
    below = [s for s in active if s["attendance"] is not None and not is_eligible(s["attendance"])]
    unrecorded = [s for s in active if s["attendance"] is None]
    print(f"\nStudents below {MIN_ATTENDANCE}% attendance:")
    if below:
        for s in below:
            print(f"  {s['id']}  {s['name']:<20} {s['attendance']:g}%")
    else:
        print("  None")
    if unrecorded:
        print(f"  ({len(unrecorded)} student(s) have no attendance recorded yet)")


def menu_count_eligible(students):
    active = active_students(students)
    if not active:
        print("  [!] No active students registered yet.")
        return
    eligible = sum(1 for s in active if is_eligible(s["attendance"]))
    print(f"  Eligible for semester examination: {eligible} of {len(active)} active students.")


def menu_attendance(students):
    run_submenu("Attendance", {
        "1": ("Record / update attendance", menu_set_attendance),
        "2": ("View attendance & eligibility", menu_view_attendance),
        "3": (f"Students below {MIN_ATTENDANCE}%", menu_below_attendance),
        "4": ("Count eligible students", menu_count_eligible),
    }, students)


# --- Marks ------------------------------------------------------------------
def menu_enter_all_marks(students):
    student = ask_for_student(students)
    if student is None:
        return
    for subject in SUBJECTS:
        student["marks"][subject] = read_number(f"  {subject} mark (0-100): ", 0, 100)
    print(f"  [OK] Marks saved for {student['name']}.")


def menu_update_one_mark(students):
    student = ask_for_student(students)
    if student is None:
        return
    subject = choose_subject()
    student["marks"][subject] = read_number(f"  New {subject} mark (0-100): ", 0, 100)
    print(f"  [OK] {subject} mark updated to {student['marks'][subject]:g}.")


def menu_view_subject_mark(students):
    student = ask_for_student(students)
    if student is None:
        return
    subject = choose_subject()
    mark = student["marks"].get(subject)
    if mark is None:
        print(f"  {subject} mark has not been recorded for {student['name']}.")
    else:
        print(f"  {student['name']} - {subject}: {mark:g}")


def menu_academic_summary(students):
    student = ask_for_student(students)
    if student is not None:
        display_academic_summary(student)


def menu_marks(students):
    run_submenu("Marks", {
        "1": ("Enter marks for all subjects", menu_enter_all_marks),
        "2": ("Update one subject's mark", menu_update_one_mark),
        "3": ("View mark for a subject", menu_view_subject_mark),
        "4": ("Academic summary", menu_academic_summary),
    }, students)


# --- Result -----------------------------------------------------------------
def menu_individual_result(students):
    student = ask_for_student(students)
    if student is not None:
        display_result(student)


def menu_all_results(students):
    active = active_students(students)
    if not active:
        print("  [!] No active students to process.")
        return
    print(f"\n{'ID':<8}{'Name':<20}{'Att%':>7}  {'Exam':<13}{'Total':>7}{'Avg':>8}  {'Result':<9}{'Grade':<7}Remarks")
    print("-" * 100)
    for s in active:
        result = build_result(s)
        att = "-" if s["attendance"] is None else f"{s['attendance']:g}"
        if result is None:
            print(f"{s['id']:<8}{s['name']:<20}{att:>7}  {eligibility_text(s['attendance']):<13}"
                  f"{'-':>7}{'-':>8}  {'Pending':<9}{'-':<7}Marks incomplete")
            continue
        remark = "Failed in: " + ", ".join(result["failed"]) if result["failed"] else "All subjects passed"
        print(f"{s['id']:<8}{s['name']:<20}{att:>7}  {eligibility_text(s['attendance']):<13}"
              f"{result['total']:>7g}{result['average']:>8.2f}  {result['result']:<9}{result['grade']:<7}{remark}")


def menu_result(students):
    run_submenu("Examination Result", {
        "1": ("Result for one student", menu_individual_result),
        "2": ("Summary for all active students", menu_all_results),
    }, students)


# --- Department information -------------------------------------------------
def menu_show_departments(_students):
    display_departments()


def menu_validate_department(_students):
    code = input("Enter department code to validate: ").strip()
    if is_valid_department(code):
        print(f"  [OK] {code} is valid - {DEPARTMENTS[code]}.")
    else:
        print(f"  [!] '{code}' is not a valid department. Valid codes: {', '.join(DEPARTMENTS)} (case-sensitive).")


def menu_departments_in_use(students):
    active = active_students(students)
    if not active:
        print("  [!] No active students registered yet.")
        return
    represented = {s["department"] for s in active}
    empty = set(DEPARTMENTS) - represented
    print(f"  Departments with registered students: {', '.join(sorted(represented))}")
    print(f"  Departments with no students yet    : {', '.join(sorted(empty)) or 'None'}")


def menu_departments(students):
    run_submenu("Department Information", {
        "1": ("Display available departments", menu_show_departments),
        "2": ("Validate a department code", menu_validate_department),
        "3": ("Departments represented by students", menu_departments_in_use),
    }, students)


# --- Statistics -------------------------------------------------------------
def menu_batch_statistics(students):
    stats = compute_statistics(students)
    if stats["total"] == 0:
        print("  [!] No active students registered yet - nothing to report.")
        return
    print("\nStudent statistics (active students only)")
    print(f"  Total students         : {stats['total']}")
    print("  Students per department:")
    for dept, count in sorted(stats["per_department"].items()):
        print(f"    {dept:<6}: {count}")
    print(f"  Unique departments     : {', '.join(sorted(stats['departments']))}")
    print(f"  Eligible for exam      : {stats['eligible']}")
    if stats["pending"]:
        print(f"  Results pending        : {stats['pending']} (marks incomplete)")
    if stats["highest"] is None:
        print("  Failed / averages      : not available until marks are entered")
        return
    print(f"  Students who failed    : {stats['failed']}")
    print(f"  Highest average        : {stats['highest'][0]:.2f} ({stats['highest'][2]}, {stats['highest'][1]})")
    print(f"  Lowest average         : {stats['lowest'][0]:.2f} ({stats['lowest'][2]}, {stats['lowest'][1]})")
    print(f"  Batch average          : {stats['batch_average']:.2f}")


def menu_students_in_course(students):
    if not active_students(students):
        print("  [!] No active students registered yet.")
        return
    course = read_course("Course name: ")
    group = students_in_course(students, course)
    if group:
        print(f"  {len(group)} student(s) registered for {course}: {', '.join(sorted(group))}")
    else:
        print(f"  No active students are registered for {course}.")


def menu_statistics(students):
    run_submenu("Student Statistics", {
        "1": ("Batch statistics", menu_batch_statistics),
        "2": ("Students registered for a course", menu_students_in_course),
    }, students)


# --- Withdrawal -------------------------------------------------------------
def menu_withdrawal(students):
    student = ask_for_student(students)
    if student is None:
        return
    print("\nRecord to be withdrawn:")
    display_student(student)
    if not confirm(f"\nConfirm withdrawal of {student['id']} - {student['name']}? (y/n): "):
        print("  Withdrawal cancelled. No changes made.")
        return
    student["status"] = WITHDRAWN
    print(f"  [OK] {student['name']} withdrawn. Record kept for audit; excluded from active processing.")


# --- Demo data (optional, for quick testing) ---------------------------------
def menu_load_demo(students):
    demo = [
        ("ST101", "Arun Kumar", "CSE", 2, "arun.kumar@nova.edu", "9876500101", 92,
         {"Python": 85, "SQL": 78, "Excel": 92, "Power BI": 81}, ["Python Training"]),
        ("ST102", "Divya Lakshmi", "IT", 3, "divya.l@nova.edu", "9876500102", 75,
         {"Python": 72, "SQL": 68, "Excel": 75, "Power BI": 70}, ["Python Training", "SQL Training"]),
        ("ST103", "Karthik Raj", "AI&DS", 1, "karthik.r@nova.edu", "9876500103", 60,
         {"Python": 45, "SQL": 38, "Excel": 52, "Power BI": 40}, ["Python Training", "SQL Training"]),
        ("ST104", "Meena Sundaram", "ECE", 4, "meena.s@nova.edu", "9876500104", 88.5,
         {"Python": 95, "SQL": 91, "Excel": 98, "Power BI": 93}, ["SQL Training"]),
        ("ST105", "Naveen Prasad", "BBA", 2, "naveen.p@nova.edu", "9876500105", 74,
         {"Python": 58, "SQL": 62, "Excel": 55, "Power BI": 65}, ["Python Training"]),
        ("ST106", "Sneha Reddy", "CSE", 3, "sneha.r@nova.edu", "9876500106", 81,
         {"Python": 78, "SQL": 49, "Excel": 85, "Power BI": 80}, ["SQL Training"]),
    ]
    loaded = 0
    for sid, name, dept, year, email, phone, attendance, marks, courses in demo:
        record = create_student(sid, name, dept, year, email, phone)
        record["attendance"] = attendance
        record["marks"] = dict(marks)
        record["courses"] = set(courses)
        if register_student(students, record):
            loaded += 1
    print(f"  [OK] {loaded} demo student(s) loaded ({len(demo) - loaded} skipped - ID already exists).")


# ----------------------------------------------------------------------------
# MAIN PROGRAM
# ----------------------------------------------------------------------------
def print_main_menu():
    print("\n" + "=" * 48)
    print("  NOVA UNIVERSITY - STUDENT SERVICE PORTAL")
    print("=" * 48)
    print("  1. Student Registration")
    print("  2. Student Search")
    print("  3. Course Registration")
    print("  4. Attendance")
    print("  5. Marks")
    print("  6. Result")
    print("  7. Department Information")
    print("  8. Student Statistics")
    print("  9. Student Withdrawal")
    print(" 10. Load demo data (for testing)")
    print("  0. Exit")


def main():
    students = {}  # {student_id: record}
    actions = {
        "1": menu_registration,
        "2": menu_search,
        "3": menu_courses,
        "4": menu_attendance,
        "5": menu_marks,
        "6": menu_result,
        "7": menu_departments,
        "8": menu_statistics,
        "9": menu_withdrawal,
        "10": menu_load_demo,
    }
    while True:
        print_main_menu()
        choice = input("Select an option: ").strip()
        if choice == "0":
            print("Thank you for using the Student Service Portal. Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("  [!] Invalid selection. Please choose a number from the menu.")
            continue
        action(students)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended. Goodbye!")
