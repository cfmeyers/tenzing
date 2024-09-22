# tenzing

A utility for interacting with Basecamp 4


# TODO
- [X] add command get-todos-for-user 
    - [X] put user_id in the config.toml file, parse it in config.py
    - [X] has a --cached flag for getting from db
    - [X] if --cached not passed, fetches from basecamp and saves to db
    - [X] have a --json flag to output the todos in json format, otherwise pretty print with rich

- [X] Implement "current todo" feature
    - [X] Update SQLite database schema
        - [X] Add a new table named 'current_todo_history' with fields: todo_id, made_current_todo_at
    - [X] Update db.py
        - [X] Add functions to insert new current todo
        - [X] Add function to get the current todo (most recent entry)
    - [X] Update cli.py
        - [X] Add get-current-todo command
            - [X] Retrieve the current todo from the database
            - [X] Display the todo details (consider reusing the display logic from get-todos-for-user)
        - [X] Add set-current-todo command
            - [X] Accept a todo_id as an argument
            - [X] Insert a new entry into the current_todo_history table
