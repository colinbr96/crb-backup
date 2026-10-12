from src.utils.user_input import input_option, input_yes_no


def test_input_option_returns_valid_response(fake_input):
    fake_input("b")
    assert input_option("Pick: ", ["a", "b"]) == "b"


def test_input_option_strips_whitespace(fake_input):
    fake_input("  a \n")
    assert input_option("Pick: ", ["a", "b"]) == "a"


def test_input_option_reprompts_on_invalid_input(fake_input, capsys):
    fake_input("x", "", "a")
    assert input_option("Pick: ", ["a", "b"]) == "a"
    assert capsys.readouterr().out.count("Invalid input. Please enter (a/b).") == 2


def test_input_yes_no_yes(fake_input):
    fake_input("y")
    assert input_yes_no("Continue? ") is True


def test_input_yes_no_no(fake_input):
    fake_input("n")
    assert input_yes_no("Continue? ") is False


def test_input_yes_no_is_case_sensitive(fake_input):
    fake_input("Y", "y")
    assert input_yes_no("Continue? ") is True
