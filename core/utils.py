"""
Utils functions
"""
import re

regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


# Define a function for validating an Email
def check_email(email):
    if re.fullmatch(regex, email):
        return True
    else:
        return False
