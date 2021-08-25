#!/usr/bin/env python
# encoding: utf-8
# Author: Psycho_Coder <https://psychocoder.github.io/>

from re import match
from sys import stdout, hexversion, exit, argv
import traceback

TITLE = """
  _    _           _       _____    _            _   _  __ _
 | |  | |         | |     |_   _|  | |          | | (_)/ _(_)
 | |__| | __ _ ___| |__     | |  __| | ___ _ __ | |_ _| |_ _  ___ _ __
 |  __  |/ _` / __| '_ \    | | / _` |/ _ \ '_ \| __| |  _| |/ _ \ '__|
 | |  | | (_| \__ \ | | |  _| || (_| |  __/ | | | |_| | | | |  __/ |
 |_|  |_|\__,_|___/_| |_| |_____\__,_|\___|_| |_|\__|_|_| |_|\___|_|
 ----------------------------------------------------------------------
                                            Version: 3.4
                                            Coded By: Psycho_Coder
 ----------------------------------------------------------------------
"""

USAGE = """
Move to the folder (hashidentifier) containing the file HashIdentifier.py and then
run in terminal

    python HashIdentifier.py <Your hash>

    or

    python HashIdentifier.py

The above opens the interactive mode where you can repeatedly give hashes. To exit
from the interactive mode simple write any one of the following commands :-
                        "quit, or q, or exit, or end"

For more details please refer to the README

                2.7.x <= Python Compatibility <= 3.x.x
"""

HASHES = (
    ("MD5(Unix)", "^\$1\$.{0,8}\$[a-zA-Z0-9\/\.]{22}$"),
    (("MD5(APR)", "Apache MD5"), "^\$apr1\$.{0,8}\$[a-zA-Z0-9\/\.]{22}$"),
    ("MD5(MyBB)", "^[a-fA-F0-9]{32}:[a-z0-9]{8}$"),
    ("MD5", "^[a-fA-F0-9]{32}$"),
    (("MD5 crypt", "FreeBSD MD5", "Cisco-IOS MD5"), "^\$1\$[a-zA-Z0-9./]{8}\$[a-zA-Z0-9./]{1,}$"),
    ("MD5 apache crypt", "^\$apr1\$[a-zA-Z0-9./]{8}\$[a-zA-Z0-9./]{1,}$"),
    ("MD5(Joomla)", "^[a-fA-F0-9]{32}:[a-zA-Z0-9]{16,32}$"),
    ("MD5(Wordpress)", "^\$P\$[a-zA-Z0-9\/\.]{31}$"),
    ("MD5(phpBB3)", "^\$H\$[a-zA-Z0-9\/\.]{31}$"),
    (("MD5(osCommerce)", "xt:Commerce"), "^[a-fA-F0-9]{32}:[a-zA-Z0-9]{2}$"),
    ("MD5(Palshop)", "^[a-fA-F0-9]{51}$"),
    ("MD5(IP.Board)", "^[a-fA-F0-9]{32}:.{5}$"),
    ("MD5(Chap)", "^[a-fA-F0-9]{32}:[0-9]{32}:[a-fA-F0-9]{2}$"),
    ("SHA-1(Django)", "^sha1\$.{0,32}\$[a-fA-F0-9]{40}$"),
    ("SHA-1 crypt", "^\$4\$[a-zA-Z0-9./]{8}\$[a-zA-Z0-9./]{1,}$"),
    ("SHA-1(Hex)", "^[a-fA-F0-9]{40}$"),
    ("SHA-512(Drupal)", "^\$S\$[a-zA-Z0-9\/\.]{52}$"),
    ("SHA-512 crypt", "^\$6\$[a-zA-Z0-9./]{8}\$[a-zA-Z0-9./]{1,}$"),
    ("SHA-256(Django)", "^sha256\$.{0,32}\$[a-fA-F0-9]{64}$"),
    ("SHA-256 crypt", "^\$5\$[a-zA-Z0-9./]{8}\$[a-zA-Z0-9./]{1,}$"),
    ("SHA-384(Django)", "^sha384\$.{0,32}\$[a-fA-F0-9]{96}$"),
    ("SHA-256(Unix)", "^\$5\$.{0,22}\$[a-zA-Z0-9\/\.]{43,69}$"),
    ("SHA-512(Unix)", "^\$6\$.{0,22}\$[a-zA-Z0-9\/\.]{86}$"),
    (("SHA-384", "SHA3-384", "Skein-512(384)", "Skein-1024(384)"), "^[a-fA-F0-9]{96}$"),
    (("SHA-512", "SHA-512(HMAC)", "SHA3-512", "Whirlpool", "SALSA-10", "SALSA-20", "Keccak-512", "Skein-512",
      "Skein-1024(512)"), "^[a-fA-F0-9]{128}$"),
    (("SHA-256", "SHA-256(HMAC)", "SHA-3(Keccak)", "GOST R 34.11-94", "RIPEMD-256", "HAVAL-256", "Snefru-256",
      "Snefru-256(HMAC)", "RIPEMD-256(HMAC)", "Keccak-256", "Skein-256", "Skein-512(256)"), "^[a-fA-F0-9]{64}$"),
    (("SHA-1(Oracle)", "HAVAL-192", "OSX v10.4, v10.5, v10.6", "Tiger-192", "TIGER-192(HMAC)"), "^[a-fA-F0-9]{48}$"),
    (("SHA-224", "SHA-224(HMAC)", "HAVAL-224", "Keccak-224", "Skein-256(224)", "Skein-512(224)"), "^[a-fA-F0-9]{56}$"),
    (("MD5(HMAC(Wordpress))", "MD5(HMAC)", "MD5", "RIPEMD-128", "RIPEMD-128(HMAC)", "Tiger-128", "Tiger-128(HMAC)",
      "RAdmin v2.x", "NTLM", "Domain Cached Credentials(DCC)", "Domain Cached Credentials 2(DCC2)", "MD4", "MD2",
      "MD4(HMAC)", "MD2(HMAC)", "Snefru-128", "Snefru-128(HMAC)", "HAVAL-128", "HAVAL-128(HMAC)", "Skein-256(128)",
      "Skein-512(128)", "MSCASH2"), "^[0-9A-Fa-f]{32}$"),
)


def identify_hashes(input_hash):
    """
    Function to identify all the hashes and return the results as list.
    :rtype : list
    :param input_hash:
    """
    res = []
    for items in HASHES:
        if match(items[1], input_hash):
            res += [items[0]] if isinstance(items[0], str) else items[0]
    return res


def get_input(prompt):
    """
    Function Get input from the user maintaining the python compatibility with earlier and newer versions.
    :param prompt:
    :rtype : str
    :return: Returns the Hash string received from user.
    """
    if hexversion > 0x03000000:
        return input(prompt)
    else:
        return raw_input(prompt)


def start_process():
    """
    Run infinite loop to ask for entering a hash every time a hash if found.
    """
    firstrun = True
    while True:
        print("_" * 80)
        print('\n')

        # Take the Hash as Input from the User, Or from Run Args
        if firstrun and len(argv) == 2:
            input_hash = argv[1]
            firstrun = False
        else:
            input_hash = get_input("Enter the Hash : ")
            # Trim the hash entered and remove the unwanted spaces
            input_hash = input_hash.strip()

            # Exit from loop.
            if input_hash in ("quit", "exit", "q", "end"):
                print("Bye Bye Thank you for using this tool.")
                break

        if len(input_hash) < 1:
            print("\nPlease enter the hash. No input hash found.")
        else:
            # Do the operation of Identifying the hashes.
            results = identify_hashes(input_hash)

            # If the length of the list returned by the hash identifying method is zero
            # that means no hashes algorithms have been found
            if len(results) == 0:
                print("\n\n:( Sorry we are unable to identify the type of hash.")
            elif len(results) > 2:

                # Show the results with most and less probable hash algorithms
                print("\nMost Probable Hash Algorithms found:\n")
                print("[+] " + results[0])
                print("[+] " + results[1])
                print("\nOther Possible Hash Algorithms found:\n")
                for item in range(int(len(results)) - 2):
                    print("[+] " + results[item + 2])
            else:
                print("\nMost Probable Hash Algorithms found:\n")
                for item in range(int(len(results))):
                    print("[+] " + results[item])


def main():
    """
    Print the TITLE and USAGE and then start the main loop.
    """
    print(TITLE)
    print(USAGE)
    try:
        start_process()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except EOFError:
        print("\nSystem Exited during user input.")
        traceback.print_exc(file=stdout)


if __name__ == "__main__":
    exit(main())
