import logging
import sys
from pathlib import Path

import yaml

from library.logging import LOGGER
from library.nursery import v1

if __name__ == "__main__":
    import argparse

    # Create the argument parser
    parser = argparse.ArgumentParser(description="Poshmark sharing bot.")

    # Add argument for configuration file path
    parser.add_argument(
        "-c",
        "--config-fpath",
        type=Path,
        required=True,
        help="Path to the YAML configuration file",
    )

    # Optional verbose flag
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debugging mode"
    )

    # Parse the arguments
    args = parser.parse_args()

    with open(args.config_fpath, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    posh_nursery = v1.PoshNursery(
        config["credentials"]["username"],
        config["credentials"]["password"],
        # config["sharing"]["slow_mode"],
        # args.debug,
        # config["sharing"]["check_captcha"],
        # config["sharing"]["share_closets_from_file"],
        # config["sharing"]["wait_time"],
        # config["sharing"]["maintain_order_based_on_order_file"],
        # config["sharing"]["share_back"],
    )
    try:
        posh_nursery.share_closet()
    except Exception as e:
        LOGGER.error(f"An unexpected error occured while sharing: {str(e)}")
        posh_nursery.teardown()
        sys.exit(1)
