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

- [X] Implement "create todo" feature
    - [X] Update basecamp_api.py
        - [X] Add a new function to create a todo using the Basecamp API
        - [X] Include parameters for todo content, todolist ID, and project ID
    - [X] Update cli.py
        - [X] Add create-todo command
            - [X] Accept arguments for todo title, todo body, todolist ID, and project ID
            - [X] Use the current user's ID from config.toml as the "Assigned To" user
            - [X] Call the new Basecamp API function to create the todo
            - [X] Save the new todo to the local database
            - [X] Display a success message with the new todo's details
    - [X] implement a create-todo-from-editor command
        - make a new module, edit.py, to hold this logic
        - should use the VISUAL or EDITOR environment variable to create the todo
        - should use the editor to open a temp file
        - should populate the temp file using a template with yaml frontmatter for
            - project id
            - todolist id
            - title
        - the rest of the file should be markdown.  This will be the body of the todo
        - the editor should save and exit the file, which should be read and parsed for the todo data
        - the data should then be used to create the todo using the Basecamp API
        - the new todo should be saved to the local database
        - the new todo should be displayed with the get-todos-for-user command
        - use the python-frontmatter library to parse the yaml frontmatter
        - use the Markdown library to parse the markdown body
