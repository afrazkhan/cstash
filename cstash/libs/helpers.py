"""
Helper methods that don't belong in classes
"""

from datetime import timedelta, timezone, datetime
import logging
import os
import cstash.libs.exceptions as exceptions


def datetime_this_seconds_ago(duration):
    """
    Work out the datetime [duraton] seconds ago, and return it
    """
    return (datetime.now(timezone.utc) + timedelta(seconds=-duration))

def seconds_from_hours(hours):
    """ Return number of seconds equal to [hours] """

    return (60*60)*hours

def set_logger(level='ERROR', filename=None):
    """ Set logging level to [level], and some opinionated formatting """

    logging.basicConfig(level=level, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S%z', filename=filename, filemode='w+')

def get_paths(target):
    """
    Return a list of the full paths to [target]. Note that [target] may be a directory. If it's
    only a single file, the list will have a single element. [target] can be either relative or
    absolute.
    """

    full_path = os.path.abspath(target)
    if os.path.isdir(full_path):
        import glob
        file_listing = glob.glob("{}/**".format(full_path), recursive=True)
        file_listing.pop(0)
        return [ this_file for this_file in file_listing if os.path.isfile(this_file) ]

    return [full_path]

def recreate_directories(recreate_in, filepath):
    """
    Strip the directories from [filepath], and create the paths in [recreate_in].
    Return True for success, or False for failure
    """

    try:
        os.makedirs("{}{}".format(recreate_in, os.path.dirname(filepath)), exist_ok=True)
        return True
    except Exception as e:
        logging.error(e)
        return False

def strip_path(path):
    """
    Strip the path from [path], and return a tuple with the path as the first
    element, and just the filename as the second.
    """

    if os.path.isdir(path):
        path = f"{path}/"
    return os.path.split(path)

def clear_path(path):
    """
    Ensure that [path] is clear for writing to. This means creating all necessary
    subdirectories, and handling filename deduplication tasks.

    Return the absolute clear filesystem path. This may mean a renaming of of the original
    file passed in at the end of [path]. For example:

    Return value for existing [path]/foo.txt will be [path]/foo.1.txt

    Return value for existing [path]/foo will be [path]/1.foo

    Raise a CstashCriticalException on failure
    """

    stripped_path = strip_path(path)
    directories = stripped_path[0]
    filename = stripped_path[1]
    if filename == '':
        raise exceptions.CstashCriticalException(message="helpers.clear_path() was given a " \
            "directory instead of a file")
    if not os.path.exists(directories):
        os.makedirs(directories)
    if os.path.isfile(f"{directories}/{filename}") is False:
        return path

    new_path = path
    counter = 0
    while os.path.exists(new_path):
        split_file = filename.split(".")[: len(filename.split(".")) - 1]
        extension = filename.split(".")[-1]
        counter += 1
        new_path = ".".join(split_file + [str(counter)] + [extension])
        new_path = "/".join([directories] + [new_path])

    return new_path

def delete_file(path):
    """
    Delete file at [path].

    TODO: Not sure if this should happen: Return True for success, or raise a
          CstashCriticalException on failure
    """

    os.remove(path)

def merge_dicts(dict_a, dict_b):
    """
    Override [dict_a] dict retrieved from the dict_a file with [dict_b] given on the command
    line. Also handle missing dict_b that are in neither [dict_b] or [dict_a].

    Return a dict with the updated dict_b. This should be all the key/value pairs from both
    [dict_b] and [dict_a], with the ones from [dict_b] overriding those of [dict_a].
    """

    dict_a.update( (k,v) for k,v in dict_b.items() if v is not None or (k not in dict_a))

    for k, v in dict_a.items():
        if v is None:
            raise exceptions.CstashCriticalException(message=f"{k} was not given via command line " \
                "options, or the configuration file")

    return dict_a
