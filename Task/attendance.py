while True:
        try:
            att = float(input("Enter attendance:"))
            if 0 <= att <= 100:
                print("attendance:",att)
            else:
                print("Invalid attendance")
                break
        except ValueError as Error:
            print("Invalid attendance:")