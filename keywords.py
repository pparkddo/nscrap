KEYWORDS_FILE_NAME = "keywords.txt"
ENCODING = "utf8"
ANNOTATION_MARK = "#"


def read_keywords(filename=KEYWORDS_FILE_NAME):
    with open(filename, "r", encoding=ENCODING) as file:
        keywords = file.readlines()
    keywords = _strip(keywords)
    keywords = _remove_annotation(keywords)
    keywords = _upper(keywords)
    keywords = _remove_empty(keywords)
    keywords = _drop_duplicates(keywords)
    return keywords


def is_keyword_match(title, keywords):
    return any([keyword in title.upper() for keyword in keywords])


def _strip(keywords):
    return [keyword.strip() for keyword in keywords]


def _remove_annotation(keywords):
    return list(filter(lambda keyword: not keyword.startswith(ANNOTATION_MARK), keywords))


def _upper(keywords):
    return [keyword.upper() for keyword in keywords]


def _remove_empty(keywords):
    return list(filter(lambda keyword: keyword, keywords))


def _drop_duplicates(keywords):
    return list(set(keywords))
