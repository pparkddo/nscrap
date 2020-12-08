SETTINGS_FILE_NAME = "settings.json"
ENCODING = "utf-8"


def read_settings(filename=SETTINGS_FILE_NAME, encoding=ENCODING):
    # pylint: disable=import-outside-toplevel
    import json
    with open(filename, "r", encoding=encoding) as file:
        settings = json.load(file)
    return settings
