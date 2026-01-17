import sys
from library.validation import check_bool_input
from library.nursery import PoshNursery
import yaml


if __name__ == "__main__":
    arg_count = len(sys.argv)
    wait_time = 3600  # default wait time is 1 hr
    debug = False
    slow_mode = False
    maintain_order_based_on_order_file = False
    check_captcha = True
    share_closets_from_file = False
    share_back = False
    if arg_count >= 2:
        good_format, check_captcha = check_bool_input(sys.argv[1].lower())
        if not good_format:
            print(
                "1st parameter "
                + sys.argv[1]
                + " needs to be a boolean value Y|N for whether or not to check for captcha"
            )
            print(
                "Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}"
            )
            sys.exit()
    if arg_count >= 3:
        good_format, share_closets_from_file = check_bool_input(sys.argv[2].lower())
        if not good_format:
            print(
                "2nd parameter "
                + sys.argv[2]
                + " needs to be a boolean value Y|N for whether or not to share closets in closetsToShare.txt"
            )
            print(
                "Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}"
            )
            sys.exit()
    if arg_count >= 4:
        try:
            wait_time = int(sys.argv[3])
        except ValueError:
            print(
                "3rd parameter "
                + sys.argv[3]
                + " needs to be an integer number for the number of seconds to wait after one round of sharing"
            )
            print(
                "Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}"
            )
            sys.exit()
    if arg_count >= 5:
        good_format, maintain_order_based_on_order_file = check_bool_input(
            sys.argv[4].lower()
        )
        if not good_format:
            print(
                "4th parameter "
                + sys.argv[4]
                + " needs to be a boolean value Y|N for whether or not to maintain closet order based on order file"
            )
            print(
                "Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}"
            )
            sys.exit()
    if arg_count >= 6:
        good_format, share_back = check_bool_input(sys.argv[5].lower())
        if not good_format:
            print(
                "5th parameter "
                + sys.argv[5]
                + " needs to be a boolean value Y|N for whether or not to share back"
            )
            print(
                "Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}"
            )
            sys.exit()
    if arg_count >= 7:
        print("Too many parameters. This program only takes 5 optional parameters")
        print(
            "Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}"
        )
        sys.exit()

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    username = config["username"]
    password = config["password"]
    posh_nursery = PoshNursery(
        username,
        password,
        slow_mode,
        debug,
        check_captcha,
        share_closets_from_file,
        wait_time,
        maintain_order_based_on_order_file,
        share_back,
    )
    print("Logging in Poshmark as " + username + "...")
    posh_nursery.login()
    posh_nursery.share()
    posh_nursery.quit()
