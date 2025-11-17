# Build Manifest

This manifest outlines the tools, resources, and prompts exposed by the MCP server.

## Tools

Tools are functions your MCP server exposes to AI models. They are defined in your project's build manifest.

**Build manifest → tools:** `[create_database_page, get_database, get_page, update_page, create_page, archive_page, create_task, get_tasks, complete_task, update_task, delete_task, get_projects, reopen_task, get_task, read_note, create_note, update_note, append_to_note, list_notes, search_notes, delete_note, get_note_metadata]`

### Notion Tools
- `create_database_page`: Creates a new page in a Notion database.
- `get_database`: Queries a Notion database.
- `get_page`: Retrieves a Notion page by ID.
- `update_page`: Updates properties of a Notion page.
- `create_page`: Creates a standalone Notion page.
- `archive_page`: Archives (deletes) a Notion page.

### Todoist Tools
- `create_task`: Creates a new task in Todoist.
- `get_tasks`: Retrieves tasks from Todoist.
- `complete_task`: Marks a task as completed.
- `update_task`: Updates an existing task.
- `delete_task`: Deletes a task.
- `get_projects`: Retrieves all projects.
- `reopen_task`: Reopens a completed task.
- `get_task`: Retrieves a specific task by ID.

### Obsidian Tools
- `read_note`: Reads the content of an Obsidian note.
- `create_note`: Creates a new Obsidian note.
- `update_note`: Replaces the content of an existing note.
- `append_to_note`: Appends content to a note.
- `list_notes`: Lists all notes in a folder or the entire vault.
- `search_notes`: Searches for notes containing specific text.
- `delete_note`: Deletes a note.
- `get_note_metadata`: Retrieves metadata for a note.

## Resources

Resources are data your MCP server exposes for context—files, schemas, or app-specific info. They're identified by URIs.

- `file:///main.py`
- `file:///tools/notion_tools.py`
- `file:///tools/todoist_tools.py`
- `file:///tools/obsidian_tools.py`
- `file:///.env.example`

## Resource Templates

Resource templates are parameterized resources using URI templates. They allow dynamic resource generation with placeholders.

- `file:///{obsidian_vault_path}/{note_path}`: Access an Obsidian note.
- `notion:///databases/{database_id}`: Access a Notion database.
- `notion:///pages/{page_id}`: Access a Notion page.
- `todoist:///projects/{project_id}`: Access a Todoist project.
- `todoist:///tasks/{task_id}`: Access a Todoist task.

## Prompts

Prompts are reusable message templates your MCP server exposes. They can include structured instructions and accept arguments.

- `/create_notion_page`: Creates a new page in a Notion database.
  - **Arguments**: `title` (str), `database_id` (str, optional), `properties` (dict, optional)
- `/add_todoist_task`: Adds a new task to Todoist.
  - **Arguments**: `content` (str), `description` (str, optional), `project_id` (str, optional), `due_string` (str, optional)
- `/find_in_obsidian`: Searches for notes in your Obsidian vault.
  - **Arguments**: `query` (str), `case_sensitive` (bool, optional)
- `/summarize_note`: Reads an Obsidian note and provides a summary.
  - **Arguments**: `note_path` (str)
- `/archive_notion_page`: Archives a page in Notion.
  - **Arguments**: `page_id` (str)
