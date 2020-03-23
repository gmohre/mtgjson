"""
MTGJSON simple utilities
"""
import collections
import hashlib
import itertools
import logging
import multiprocessing
import time
from typing import Any, Callable, List, Tuple, Union

import requests
import requests.adapters
import urllib3

from .consts import LOG_PATH


def url_keygen(prod_id: Union[int, str], with_leading: bool = True) -> str:
    """
    Generates a key that MTGJSON will use for redirection
    :param prod_id: Seed
    :param with_leading: Should URL be included
    :return: URL Key
    """
    return_value = "https://mtgjson.com/links/" if with_leading else ""
    return f"{return_value}{hashlib.sha256(str(prod_id).encode()).hexdigest()[:16]}"


def to_camel_case(snake_str: str) -> str:
    """
    Convert "snake_case" => "snakeCase"
    :param snake_str: Snake String
    :return: Camel String
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def init_logger() -> None:
    """
    Initialize the main system logger
    """
    LOG_PATH.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                str(
                    LOG_PATH.joinpath(
                        "mtgjson_" + str(time.strftime("%Y-%m-%d_%H.%M.%S")) + ".log"
                    )
                )
            ),
        ],
    )


def parse_magic_rules_subset(
    magic_rules: str, start_header: str, end_header: str
) -> str:
    """
    Split up the magic rules to get a smaller working subset for parsing
    :param magic_rules: Magic rules to split up
    :param start_header: Start of content
    :param end_header: End of content
    :return: Smaller set of content
    """
    # Keyword actions are found in section XXX
    magic_rules = magic_rules.split(start_header)[2].split(end_header)[0]

    # Windows line endings... yuck
    valid_line_segments = "\n".join(magic_rules.split("\r\n"))

    return valid_line_segments


def retryable_session(
    session: requests.Session = requests.Session(), retries: int = 8
) -> requests.Session:
    """
    Session with requests to allow for re-attempts at downloading missing data
    :param session: Session to download with
    :param retries: How many retries to attempt
    :return: Session that does downloading
    """
    retry = urllib3.util.retry.Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
    )

    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def parallel_call(
    function: Callable,
    args: Any,
    repeatable_args: Union[Tuple[Any, ...], List[Any]] = None,
    fold_list: bool = False,
    fold_dict: bool = False,
    force_starmap: bool = False,
    overclock: int = 1,
) -> Any:
    """
    Execute a function in parallel
    :param function: Function to execute
    :param args: Args to pass to the function
    :param repeatable_args: Repeatable args to pass with the original args
    :param fold_list: Compress the results into a 1D list
    :param fold_dict: Compress the results into a single dictionary
    :param force_starmap: Force system to use Starmap over normal selection process
    :param overclock: How many threads per CPU to create
    :return: Results from execution, with modifications if desired
    """
    with multiprocessing.Pool(multiprocessing.cpu_count() * overclock) as pool:
        if repeatable_args:
            additional_args_repeated = [
                itertools.repeat(arg) for arg in repeatable_args
            ]
            results = pool.starmap(function, zip(args, *additional_args_repeated))
        elif force_starmap:
            results = pool.starmap(function, args)
        else:
            results = pool.map(function, args)

    if fold_list:
        return list(itertools.chain.from_iterable(results))

    if fold_dict:
        return dict(collections.ChainMap(*results))

    return results