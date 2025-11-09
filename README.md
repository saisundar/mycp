# Multi-Tool FastMCP Server

A modern FastMCP server that provides seamless integration with Notion, Todoist, and Obsidian. This server aggregates multiple tool integrations into a single MCP (Model Context Protocol) server that can be used with AI assistants like Claude Desktop.

## Features

- **Notion Integration**: Create pages, query databases, update content, and manage your Notion workspace
- **Todoist Integration**: Create tasks, manage projects, track completion, and organize your to-do lists
- **Obsidian Integration**: Create, read, update, and search notes in your Obsidian vault

## Prerequisites

- Python 3.8 or higher
- Access to the following services:
  - [Notion](https://www.notion.so/) with an integration token
  - [Todoist](https://todoist.com/) with an API token
  - [Obsidian](https://obsidian.md/) vault on your local machine

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your environment variables (see below)

## Environment Setup

Copy the `.env.example` file to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

### Notion Configuration

1. Go to https://www.notion.so/my-integrations
2. Create a new integration
3. Copy the "Internal Integration Token"
4. Add it to your `.env` file:
   ```
   NOTION_TOKEN=your_integration_token_here
   ```

5. **(Optional)** Set a default database ID:
   - Open your Notion database
   - Copy the database ID from the URL (the long string after the last `/` and before the `?`)
   - Add it to your `.env` file:
     ```
     NOTION_DATABASE_ID=your_database_id_here
     ```

6. Share your database with the integration:
   - Go to your Notion database
   - Click the three dots menu (⋯) in the top right
   - Go to "Connections"
   - Add your integration

### Todoist Configuration

1. Go to https://todoist.com/app/settings/integrations
2. Scroll to "API token"
3. Copy your token
4. Add it to your `.env` file:
   ```
   TODOIST_TOKEN=your_todoist_api_token_here
   ```

### Obsidian Configuration

1. Find your Obsidian vault path:
   - Open Obsidian
   - Open the vault you want to use
   - Go to Settings → About → Vault path (or find it in your file system)
   
2. Add it to your `.env` file:
   ```
   OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
   ```

3. **(Optional)** Set a templates folder:
   ```
   OBSIDIAN_TEMPLATES_PATH=templates/
   ```

## Running the Server

### Development Mode

Run the server directly:

```bash
python main.py
```

The server will start and listen for MCP connections.

### Production Mode with Claude Desktop

To use this server with Claude Desktop, add the following to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "multi-tool-server": {
      "command": "python",
      "args": ["/path/to/your/main.py"]
    }
  }
}
```

Make sure to use the absolute path to `main.py`.

## Available Tools

### Notion Tools

#### `create_database_page`
Create a new page in a Notion database.

**Parameters:**
- `title` (required): The title of the page
- `database_id`: The ID of the database (uses NOTION_DATABASE_ID from env if not provided)
- `properties`: Additional properties as JSON or dict

**Example:**
```python
create_database_page(
    title="New Project Idea",
    properties={"Status": {"select": {"name": "In Progress"}}, "Priority": {"select": {"name": "High"}}}
)
```

#### `get_database`
Query a Notion database and return pages.

**Parameters:**
- `database_id`: The ID of the database
- `filter_json`: JSON string for filtering (Notion API format)
- `sorts`: List of sort objects

**Example:**
```python
get_database(
    filter_json='{"property": "Status", "select": {"equals": "In Progress"}}'
)
```

#### `get_page`
Get a Notion page by ID and its content.

**Parameters:**
- `page_id` (required): The ID or URL of the page

#### `update_page`
Update properties of a Notion page.

**Parameters:**
- `page_id` (required): The ID of the page to update
- `properties` (required): Properties to update

#### `create_page`
Create a standalone Notion page (not in a database).

**Parameters:**
- `title` (required): The title of the page
- `parent_page_id`: Optional parent page ID
- `content`: Optional content to add

#### `archive_page`
Archive (delete) a Notion page.

**Parameters:**
- `page_id` (required): The ID of the page to archive

### Todoist Tools

#### `create_task`
Create a new task in Todoist.

**Parameters:**
- `content` (required): Task content
- `description`: Task description
- `project_id`: Project ID
- `labels`: List of label names
- `priority`: Task priority (1-4, where 4 is highest)
- `due_string`: Human-readable due date (e.g., "tomorrow at 12:00")
- `due_date`: Specific due date in YYYY-MM-DD format

**Example:**
```python
create_task(
    content="Review project proposal",
    priority=4,
    due_string="tomorrow at 9am",
    labels=["work", "urgent"]
)
```

#### `get_tasks`
Get tasks from Todoist with optional filtering.

**Parameters:**
- `project_id`: Filter by project ID
- `filter_query`: Natural language filter (e.g., "today", "p1", "@home")
- `label`: Filter by label

**Example:**
```python
get_tasks(filter_query="today & p1")
```

#### `complete_task`
Mark a task as completed.

**Parameters:**
- `task_id` (required): The ID of the task

#### `update_task`
Update an existing task.

**Parameters:**
- `task_id` (required): The ID of the task
- `content`: New task content
- `description`: New description
- `priority`: New priority
- `due_string`: New due date

#### `delete_task`
Delete a task from Todoist.

**Parameters:**
- `task_id` (required): The ID of the task

#### `get_projects`
Get all projects from Todoist.

#### `reopen_task`
Reopen a completed task.

**Parameters:**
- `task_id` (required): The ID of the task

#### `get_task`
Get a specific task by ID.

**Parameters:**
- `task_id` (required): The ID of the task

### Obsidian Tools

#### `read_note`
Read the content of an Obsidian note.

**Parameters:**
- `note_path` (required): Path to the note (e.g., "folder/note" or "folder/note.md")

#### `create_note`
Create a new Obsidian note.

**Parameters:**
- `note_path` (required): Path for the new note
- `content` (required): Content of the note
- `overwrite`: Whether to overwrite if exists
- `frontmatter`: Optional frontmatter as YAML

**Example:**
```python
create_note(
    note_path="projects/new-idea",
    content="# Project Idea\n\nThis is my new project idea...",
    frontmatter={"tags": ["idea", "project"], "created": "2024-01-01"}
)
```

#### `update_note`
Completely replace the content of an existing note.

**Parameters:**
- `note_path` (required): Path to the note
- `content` (required): New content

#### `append_to_note`
Append content to the end of an existing note.

**Parameters:**
- `note_path` (required): Path to the note
- `content` (required): Content to append
- `add_newline`: Whether to add a newline before appending

#### `list_notes`
List all notes in a folder or entire vault.

**Parameters:**
- `folder`: Folder path relative to vault root (empty for root)

#### `search_notes`
Search for notes containing specific text.

**Parameters:**
- `query` (required): Text to search for
- `case_sensitive`: Whether search should be case sensitive

#### `delete_note`
Delete an Obsidian note.

**Parameters:**
- `note_path` (required): Path to the note

#### `get_note_metadata`
Get metadata for a note without reading its full content.

**Parameters:**
- `note_path` (required): Path to the note

## Usage Examples

### Example 1: Create a Project in Notion and Add Tasks to Todoist

```python
# Create a project page in Notion
notion_result = create_database_page(
    title="Website Redesign",
    properties={
        "Status": {"select": {"name": "In Progress"}},
        "Priority": {"select": {"name": "High"}},
        "Type": {"select": {"name": "Project"}}
    }
)

# Create related tasks in Todoist
create_task(
    content="Design homepage mockup",
    project_id="your_project_id",
    priority=3,
    due_string="next Friday"
)

create_task(
    content="Set up development environment",
    project_id="your_project_id",
    priority=2,
    labels=["setup", "development"]
)
```

### Example 2: Create Meeting Notes in Obsidian

```python
# Create meeting notes
create_note(
    note_path="meetings/2024-01-15-team-sync",
    content="""# Team Sync Meeting - Jan 15, 2024

## Attendees
- John Doe
- Jane Smith

## Agenda
1. Project updates
2. Roadmap discussion
3. Next steps

## Notes
- Project Alpha is on track
- Need to review budget for Q2
- Next meeting scheduled for Jan 22

## Action Items
- [ ] John: Prepare budget proposal
- [ ] Jane: Update project timeline
""",
    frontmatter={
        "date": "2024-01-15",
        "tags": ["meeting", "team-sync"],
        "type": "meeting-notes"
    }
)
```

### Example 3: Search and Update Notes

```python
# Search for notes about a topic
search_results = search_notes(query="project proposal", case_sensitive=False)

# Read a specific note
note_content = read_note(note_path="projects/website-redesign")

# Append new information
append_to_note(
    note_path="projects/website-redesign",
    content="\n\n## Update\nApproved by stakeholders on 2024-01-20"
)
```

## Troubleshooting

### Notion Issues

**Error: "NOTION_TOKEN environment variable is not set"**
- Make sure you've created a `.env` file
- Verify the token is correctly copied from https://www.notion.so/my-integrations
- Ensure the database is shared with your integration

**Error: "No database_id provided and NOTION_DATABASE_ID environment variable is not set"**
- Either provide a `database_id` parameter in your function call
- Or set `NOTION_DATABASE_ID` in your `.env` file
- Or share your database with the integration (see setup steps)

### Todoist Issues

**Error: "TODOIST_TOKEN environment variable is not set"**
- Get your token from https://todoist.com/app/settings/integrations
- Add it to your `.env` file

**Tasks not appearing or being created**
- Verify your project IDs are correct (use `get_projects()` to list them)
- Check that your token has the necessary permissions

### Obsidian Issues

**Error: "OBSIDIAN_VAULT_PATH environment variable is not set"**
- Find your vault path in Obsidian settings
- Add it to your `.env` file

**Error: "Obsidian vault path does not exist"**
- Verify the path is correct and accessible
- Use absolute paths (e.g., `/Users/username/Documents/Obsidian/Vault` not `~/Documents/Obsidian/Vault`)

**Notes not found**
- Check that you're using the correct relative path from your vault root
- Include subfolders if needed (e.g., `folder/subfolder/note` not just `note`)

### General Issues

**Module not found errors**
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Check that you're running the server from the correct directory

**Connection issues with Claude Desktop**
- Verify the path in your Claude Desktop config is absolute
- Check that Python is in your system PATH
- Restart Claude Desktop after config changes

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Your API tokens provide access to your data - protect them accordingly
- Consider using a dedicated integration token for each service rather than your personal tokens

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this in your own projects.