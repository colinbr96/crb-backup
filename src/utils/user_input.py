def input_yes_no(text: str):
    response = input_option(text, ["y", "n"])
    return response == "y"


def input_option(text: str, options: list[str]):
    while True:
        response = input(text).strip()
        if response in options:
            return response
        print(f"Invalid input. Please enter ({'/'.join(options)}).")
