# Wikimedia is strict about using fancy apostrophe ’
# and left and right quotes “ ” in content and URLs.

# Apply these transforms right on the raw mastervault
# or skyjedi JSON.

import re

def force(text):
    if not text:
        return text
    return force_fancy_apostrophe(
        force_fancy_quotes(
            text
        )
    )

def force_fancy_apostrophe(text):
    if "'" in text:
        print('Force fancy apostrophe')
        print(text)
    return re.sub(r"'", r"’", text)
    
def force_fancy_quotes(text):
    if '"' in text:
        print('Force fancy quotes')
        print(text)

    # Look for a simple quote that has whitespace
    # or beginning of line on the left. Also if
    # there is a right fancy on the left, switch
    # that, too.
    # \s is "yes a whitespace character"
    # \S is "not a whitespace character"
    left = re.sub(r'(^|\s)("|”)(\S)', r'\1“\3', text)

    # Look for a simple quote that has whitespace
    # or end of line on the right. Also if there is
    # a left fancy on the right, switch it.
    right = re.sub(r'(\S)("|“)(\s|$)', r'\1”\3', left)

    return right
