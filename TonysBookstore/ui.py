class Menu:
    def __init__(self):
        self.__options = []

    def add_options(self, options: list):
        if not isinstance(options, list):
            raise ValueError("Put list of str only!!")
        if not all(isinstance(item, str) for item in options):
            raise ValueError("All list elements must be str only!!")
        self.__options.extend(options)

    def show_options(self):
        print("Choose what you want: ", *(f'{num}. {opt}' for num, opt in enumerate(self.__options, 1)), sep="\n")
        while True:
            try:
                your_selection = int(input("Your choice by number: "))
                if not 0 < your_selection <= len(self.__options):
                    raise IndexError("Your input should be in a range of these numbers only!!")
                return your_selection
            except ValueError:
                print("For your input use numbers only!!")
            except IndexError as e:
                print(e)

