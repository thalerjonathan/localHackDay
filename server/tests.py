from database import *


def get_pass_string(passed):
    if passed:
        return "PASS"
    return "FAIL"


def run_db_tests():
    email = "james@hey.com"
    password = "password"
    display_name = "JJ"

    pass_string = get_pass_string(not db_user_exists(email))
    print("[{0}]: User Does Not Exist - {1}".format(pass_string, email))

    db_add_user(email, password, display_name)
    print("[----]: Added User - {0}".format(email))

    pass_string = get_pass_string(db_user_exists(email))
    print("[{0}]: User Exists - {1}".format(pass_string, email))

    wrong_password = "thispasswordiswrong"
    pass_string = get_pass_string(not db_validate_user(email, wrong_password))
    print("[{0}]: Wrong Password is Invalid for {1}".format(pass_string, email))

    pass_string = get_pass_string(db_validate_user(email, password))
    print("[{0}]: Correct Password is Valid for {1}".format(pass_string, email))

    # Clean up
    conn = db_connect()

    with conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE email = ?)', email)


if __name__ == "__main__":
    run_db_tests()