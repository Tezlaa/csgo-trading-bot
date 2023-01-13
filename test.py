def test(msg):
    name = msg
    print(f'Привет, {name if not name == "None" else "NONE hello"}')
    

if __name__ == "__main__":
    test(input("write text: "))