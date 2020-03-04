from datetime import timedelta, timezone, datetime
from time import strftime
import logging
import os

# Take a duration in seconds and work out the datetime value for the datetime at that date and time ago
def datetime_this_seconds_ago(duration):
    return (datetime.now(timezone.utc) + timedelta(seconds=-duration))

def seconds_from_hours(hours):
    return (60*60)*hours

def log(message):
  print(message)

def set_logger(level='INFO'):
    return logging.basicConfig(level=level, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S%z')

def get_paths(file):
    """
    Return a list of the full paths to [file]. Note that [file] may be a directory. If it's
    only a single file, the list will have a single element.

    [file] can be relative or absolute.
    """

    full_path = "{}/{}".format(os.getcwd(), file)
    if os.path.isdir(full_path):
        import glob
        return glob.glob("{}/**".format(full_path), recursive=True)
    else:
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
