import bcrypt
to_reset = input("reset data? ('y' or 'n'): ")[0]
if to_reset == 'n':
    users = open("users.txt", "a")
else:
    users = open("users.txt", "w")
while True:
    print("ENTER 'exit' TO CLOSE REGISTER")
    us = input("enter username to register:").replace(" ", "")
    if us == "exit":
        print("goodbye!")
        users.close()
        exit()

    password = input(f"enter password to {us}:").replace(" ", "").encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
    users.write("|".join([us, password]) + "\n")

