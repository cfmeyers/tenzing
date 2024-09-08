# tenzing

A utility for interacting with Basecamp 4


# TODO
- [X] add command get-todos-for-user 
    - [X] put user_id in the config.toml file, parse it in config.py
    - [X] has a --cached flag for getting from db
    - [X] if --cached not passed, fetches from basecamp and saves to db
    - [X] have a --json flag to output the todos in json format, otherwise pretty print with rich
