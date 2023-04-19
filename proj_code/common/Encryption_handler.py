import rsa


def get_keys(key=500):
    pb, pr = rsa.newkeys(key)
    return {"pb": pb, "pr": pr}


def encrypt(msg, pb):
    return rsa.encrypt(msg.encode(), pb)


def decrypt(bmsg, pr):
    return rsa.decrypt(bmsg, pr).decode()


def save_public(pb):
    return pb.save_pkcs1("DER")


def load_public(bpb):
    return rsa.PublicKey.load_pkcs1(bpb, "DER")


def example(msg):
    d = get_keys()

    print("_______encrypt example_______")
    print(msg, '\033[32m', "\tthe message", '\033[0m', end="\n\n")
    e = encrypt(msg, d["pb"])
    print(e, '\033[32m', "\tthe encrypted message", '\033[0m', end="\n\n")
    print(decrypt(e, d["pr"]), end="\n")
    print('\033[32m', "\rdecrypted message", '\033[0m')
    print("_____________________________")

    print("________public sending __________")
    print(d["pb"], '\033[32m', "\tthe key", '\033[0m', end="\n\n")
    spb = save_public(d["pb"])
    print(spb, '\033[32m', "\tsomthing you can send over server", '\033[0m', end="\n\n")
    print(load_public(spb), '\033[32m', "\trestored key", '\033[0m')
    print("_________________________________")


def main():
    example("hi, my name is itamar")


if __name__ == '__main__':
    main()
