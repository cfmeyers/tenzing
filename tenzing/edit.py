import os
import tempfile
import subprocess
import frontmatter
import markdown
from tenzing.models import TodoItemView
from tenzing.basecamp_api import BasecampAPI
from tenzing.persist import save_to_db
from tenzing.config import read_config


def get_editor():
    return os.environ.get("VISUAL") or os.environ.get("EDITOR", "vim")


def create_todo_template(todolist_id=None):
    return f"""---
project_id: 
todolist_id: {todolist_id or ''}
title: 
---

Enter your todo description here in Markdown format.
"""


def edit_todo(todolist_id=None):
    editor = get_editor()
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".md", delete=False
    ) as temp_file:
        temp_file.write(create_todo_template(todolist_id))
        temp_file.flush()
        temp_file_path = temp_file.name

    try:
        subprocess.call([editor, temp_file_path])

        with open(temp_file_path, "r") as file:
            post = frontmatter.load(file)

        project_id = post.get("project_id")
        todolist_id = post.get("todolist_id")
        title = post.get("title")
        body = markdown.markdown(post.content)

        if not all([project_id, todolist_id, title]):
            raise ValueError("Project ID, Todolist ID, and Title are required.")

        config = read_config()
        assignee_id = config.user_id

        # Create todo using Basecamp API
        api = BasecampAPI()
        new_todo = api.create_todo(project_id, todolist_id, title, body, assignee_id)

        # Save todo to local database
        todo_view = TodoItemView.from_api_data(new_todo)
        save_to_db([todo_view])

        return todo_view

    finally:
        os.unlink(temp_file_path)


def create_todo_from_editor(todolist_id=None):
    try:
        new_todo = edit_todo(todolist_id)
        print(f"Todo created successfully: {new_todo.title}")
        return new_todo
    except Exception as e:
        print(f"Error creating todo: {str(e)}")
        return None
