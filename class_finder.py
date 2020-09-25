#!/usr/bin/python3
"""
This is a program to implement class finder functionality
in a similar way to the Intellij IDEA Ctrl+N search.
Input -> ./class-finder <filename> '<pattern>'
filename -> filename refers to the file containing class names separated by line breaks
pattern ->
* must include class name camelcase upper case letters
in the right order and it may contain lower case letters to narrow down the search results,
for example `'FB'`, `'FoBa'` and `'FBar'` searches must all match
`a.b.FooBarBaz` and `c.d.FooBar` classes.

* Upper case letters written in the wrong order will not find any results, for example
`'BF'` will not find `c.d.FooBar`.

* If the search pattern consists of only lower case characters then the search becomes
case insensitive (`'fbb'` finds `FooBarBaz` but `'fBb'` will not).

* If the search pattern ends with a space `' '` then the last word in the pattern must
also be the last word of the found class name (`'FBar '` finds `FooBar` and `FooBarzoo` but not `FooBarBaz`).

* The search pattern may include wildcard characters `'*'` which match missing letters
(`'B*rBaz'` finds `FooBarBaz`i but `BrBaz` does not).

The found class names must be sorted in alphabetical order ignoring package names
(package names must still be included in the output).
"""
# Import sys package to access command line arguments
import sys

# If not all required arguments are provided,
if len(sys.argv) != 3:
    print("Please specify both filename and pattern to search for!")
    sys.exit()

# If pattern specified does not contain any characters other than whitespaces
if sys.argv[2].isspace():
    print("Pattern must contain at least one alphabetical character!")
    sys.exit()

# Global variables
filename = sys.argv[1]
query = sys.argv[2]

upper_case_query = ""
full_word_queries = []
full_word_query = ""
class_names = []
last_word = False


def expand_query(query_str):
    """
    Expand the raw query string to generate term queries that can be used to search the documents
    :param query_str: the raw input query that needs to be expanded.
    UpperCased query if raw query contains only lower case characters.
    :return: all possible term queries that include
    * upper_case_query - the sequence of upper case letters that needs to be present in the class name
    * full_word_queries - List of words or substrings that are to be present in the class name
    """
    index = 0
    word_index = -1
    index_reset = False
    for ch in query_str:
        global full_word_query
        if ch == " ":
            if index == len(query_str) - 1:
                global last_word
                last_word = True
            index += 1
            continue
        if not ch.isalpha() and ch != "*":
            index += 1
            continue
        if not ch.isupper():
            if word_index >= 0:
                if index_reset:
                    full_word_query = query_str[word_index:index + 1]
                    index_reset = False
                else:
                    full_word_query += query_str[index]
            index += 1
            continue
        word_index = index
        index_reset = True
        global upper_case_query
        upper_case_query = upper_case_query + ch
        if full_word_query != "":
            full_word_queries.append(full_word_query)
        full_word_query = ""
        index += 1
    if full_word_query != "":
        full_word_queries.append(full_word_query)
    full_word_query = ""


def preprocess_text(text):
    """
    Pre process text lines in the file to remove unwanted characters and separate class names
    :param text: raw line in the file
    :return: class name separated from the namespaces
    """
    global class_names
    text = text.replace(" ", "")
    text = text.replace("\n", "")
    reversed_text = text[::-1]
    class_text = ""
    for ch in reversed_text:
        if ch == " " or ch == "\n":
            continue
        if ch == ".":
            break
        class_text += ch
    if class_text != "":
        return {"class_name": class_text[::-1], "text": text}
    return None


def check_camel_case(class_name):
    """
    check if the sequence of upper case characters in the query
    matches the camel case in the class name
    :param class_name: camel case class name
    :return: true if the sequence is present, false otherwise
    """
    case_index = 0
    for ch in class_name:
        if ch == upper_case_query[case_index]:
            case_index += 1
            if case_index == len(upper_case_query):
                return True
    return False


def compare_words(class_text, query_term):
    """
    compare character sequences in class name against characters in sub string query.
    If there is a wild card character, handle it by treating it as a match.
    :param class_text: sub string in the class name
    :param query_term: sub string query e.g., Foo
    :return: true if the substring query is present in the substring of class name, false otherwise
    """
    term_index = 0
    for ch in class_text:
        if term_index == len(query_term):
            return True
        if ch != query_term[term_index]:
            if query_term[term_index] == "*":
                if term_index == len(query_term) - 1:
                    return True
                if ch == query_term[term_index + 1]:
                    term_index += 2
                else:
                    continue
            else:
                return False
        else:
            term_index += 1
    if term_index == len(query_term):
        return True
    return False


def check_word_query(class_name, word_queries=full_word_queries):
    """
    check if the class name contains all the substring specified in the query
    :param class_name: camel case class name
    :param word_queries: list of sub string term queries
    :return: true if the class name contains all the sub string queries, false otherwise
    """
    word_index = 0
    word = ""
    for ch in class_name:
        if ch.isupper():
            if word_index == len(word_queries):
                return False
            else:
                word = ch
        else:
            if word_index == len(word_queries):
                continue
            word += ch
        if word_index == len(word_queries) and ch.isupper():
            return False
        if compare_words(word, word_queries[word_index]):
            word_index += 1
            word = ""
            if word_index == len(word_queries):
                if last_word:
                    continue
                return True
    if word_index == len(word_queries):
        return True
    return False


def check_lower_case_pattern(class_text, query_str):
    """
    look for partial or full matches for the class name text recursively
    :param class_text: camel case class name or sliced class name for partial matches
    :param query_str: lower case raw input query
    :return: true if the class name substring matches the lower case query, false otherwise
    """
    term_index = 0
    index = 0
    found = False
    for ch in class_text:
        if term_index == 0 and query_str[term_index] == "*":
            term_index += 1
        if not found:
            if ch.isupper() and ch == query_str[term_index].upper():
                found = True
                term_index += 1
            index += 1
            continue
        else:
            if term_index == len(query_str):
                return True
            if query_str[term_index] == "*":
                return compare_words(class_text[index - 1:].lower(), query_str[term_index:])
            if ch == query_str[term_index]:
                term_index += 1
                index += 1
                continue
            return check_lower_case_pattern(class_text[index:], query_str[term_index:])
    if term_index == len(query_str):
        return True
    return False


def main():
    """
    This is the entry point for the application
    """
    results = []
    expand_query(query)
    if upper_case_query == "":
        expand_query(query.upper())
    try:
        with open(filename, "r") as ip_file:
            lines = ip_file.readlines()
            for line in lines:
                processed_text = preprocess_text(line)
                if processed_text is None:
                    continue
                class_name_text = processed_text["class_name"]
                full_text = processed_text["text"]
                if check_camel_case(class_name_text):
                    if len(full_word_queries) > 0 and not check_word_query(class_name_text, full_word_queries):
                        if not check_word_query(class_name_text.lower(), [query.lower()]):
                            continue
                    results.append({"class_name": class_name_text, "full_text": full_text})
                    continue
                if check_lower_case_pattern(class_name_text, query.lower()):
                    results.append({"class_name": class_name_text, "full_text": full_text})
        if len(results) > 0:
            results = sorted(results, key=lambda i: i['class_name'].lower())
            for result in results:
                print(result["full_text"])
        else:
            print("No results found!!")
    except IOError:
        print("File not found! or File cannot be processed!")
        sys.exit()


if __name__ == "__main__":
    main()
