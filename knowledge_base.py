WINDOWS_SYSTEM = {
    "shortcuts": {
        "open_start_menu": ["win"],
        "search": ["win"],
        "file_explorer": ["win", "e"],
        "settings": ["win", "i"],
        "lock_screen": ["win", "l"],
        "desktop": ["win", "d"],
        "task_manager": ["ctrl", "shift", "esc"],
        "run_dialog": ["win", "r"],
        "screenshot": ["win", "shift", "s"],
        "virtual_desktop": ["win", "ctrl", "d"],
        "switch_window": ["alt", "tab"],
        "close_window": ["alt", "f4"],
        "minimize": ["win", "down"],
        "maximize": ["win", "up"]
    },
    "apps": {
        "notepad": "notepad",
        "calculator": "calc",
        "paint": "mspaint",
        "file_explorer": "explorer",
        "cmd": "cmd",
        "powershell": "powershell",
        "task_manager": "taskmgr",
        "control_panel": "control",
        "registry": "regedit",
        "disk_cleanup": "cleanmgr"
    },
    "file_operations": {
        "new_file": ["ctrl", "n"],
        "open_file": ["ctrl", "o"],
        "save_file": ["ctrl", "s"],
        "save_as": ["ctrl", "shift", "s"],
        "print": ["ctrl", "p"],
        "undo": ["ctrl", "z"],
        "redo": ["ctrl", "y"],
        "cut": ["ctrl", "x"],
        "copy": ["ctrl", "c"],
        "paste": ["ctrl", "v"],
        "select_all": ["ctrl", "a"],
        "find": ["ctrl", "f"],
        "replace": ["ctrl", "h"],
        "delete": ["delete"],
        "rename": ["f2"],
        "properties": ["alt", "enter"]
    }
}

MICROSOFT_WORD = {
    "shortcuts": {
        "new_document": ["ctrl", "n"],
        "open": ["ctrl", "o"],
        "save": ["ctrl", "s"],
        "save_as": ["ctrl", "shift", "s"],
        "print": ["ctrl", "p"],
        "undo": ["ctrl", "z"],
        "redo": ["ctrl", "y"],
        "bold": ["ctrl", "b"],
        "italic": ["ctrl", "i"],
        "underline": ["ctrl", "u"],
        "copy": ["ctrl", "c"],
        "cut": ["ctrl", "x"],
        "paste": ["ctrl", "v"],
        "select_all": ["ctrl", "a"],
        "find": ["ctrl", "f"],
        "replace": ["ctrl", "h"],
        "spell_check": ["f7"],
        "word_count": ["ctrl", "shift", "g"],
        "zoom_in": ["ctrl", "alt", "equal"],
        "zoom_out": ["ctrl", "alt", "minus"],
        "full_screen": ["alt", "v", "u"],
        "header": ["alt", "n", "h"],
        "footer": ["alt", "n", "o"],
        "insert_table": ["alt", "n", "t"],
        "insert_image": ["alt", "n", "p"],
        "page_break": ["ctrl", "enter"],
        "line_spacing": ["ctrl", "1"],
        "center_text": ["ctrl", "e"],
        "left_align": ["ctrl", "l"],
        "right_align": ["ctrl", "r"],
        "justify": ["ctrl", "j"]
    },
    "menus": {
        "file": "Top left — File menu",
        "home": "First ribbon tab — formatting options",
        "insert": "Second ribbon tab — tables, images, links",
        "design": "Third ribbon tab — themes and styles",
        "layout": "Fourth ribbon tab — margins, orientation",
        "references": "Fifth ribbon tab — table of contents, citations",
        "mailings": "Sixth ribbon tab — mail merge",
        "review": "Seventh ribbon tab — spelling, track changes",
        "view": "Eighth ribbon tab — zoom, reading mode"
    },
    "common_tasks": {
        "change_font": "Home tab → Font dropdown (shows current font name)",
        "change_font_size": "Home tab → Font size box (shows current size)",
        "change_color": "Home tab → Font Color button (A with color underneath)",
        "insert_table": "Insert tab → Table button → drag to select size",
        "insert_image": "Insert tab → Pictures → This Device",
        "add_header": "Insert tab → Header → choose style",
        "add_footer": "Insert tab → Footer → choose style",
        "track_changes": "Review tab → Track Changes button",
        "add_comment": "Review tab → New Comment button",
        "export_pdf": "File → Export → Create PDF/XPS"
    }
}

MICROSOFT_EXCEL = {
    "shortcuts": {
        "new_workbook": ["ctrl", "n"],
        "open": ["ctrl", "o"],
        "save": ["ctrl", "s"],
        "save_as": ["ctrl", "shift", "s"],
        "print": ["ctrl", "p"],
        "undo": ["ctrl", "z"],
        "redo": ["ctrl", "y"],
        "copy": ["ctrl", "c"],
        "cut": ["ctrl", "x"],
        "paste": ["ctrl", "v"],
        "select_all": ["ctrl", "a"],
        "find": ["ctrl", "f"],
        "replace": ["ctrl", "h"],
        "bold": ["ctrl", "b"],
        "italic": ["ctrl", "i"],
        "underline": ["ctrl", "u"],
        "new_sheet": ["shift", "f11"],
        "go_to_cell": ["ctrl", "g"],
        "formula_bar": ["f2"],
        "sum": ["alt", "equal"],
        "insert_row": ["ctrl", "shift", "plus"],
        "delete_row": ["ctrl", "minus"],
        "hide_row": ["ctrl", "9"],
        "unhide_row": ["ctrl", "shift", "9"],
        "autofit_column": ["alt", "h", "o", "i"],
        "insert_chart": ["alt", "n", "r"],
        "pivot_table": ["alt", "n", "v"],
        "filter": ["ctrl", "shift", "l"],
        "freeze_panes": ["alt", "w", "f", "f"],
        "format_cells": ["ctrl", "1"]
    },
    "common_tasks": {
        "sum_column": "Click empty cell below data → press Alt+= → Enter",
        "create_chart": "Select data → Insert tab → Charts → choose type",
        "pivot_table": "Select data → Insert tab → PivotTable",
        "sort_data": "Select column → Data tab → Sort A to Z or Z to A",
        "filter_data": "Select header → Data tab → Filter → click dropdown",
        "vlookup": "=VLOOKUP(lookup_value, table_array, col_index, FALSE)",
        "if_formula": "=IF(condition, value_if_true, value_if_false)",
        "count_formula": "=COUNT(range) for numbers, =COUNTA(range) for all",
        "average_formula": "=AVERAGE(range)",
        "conditional_format": "Home tab → Conditional Formatting → New Rule",
        "freeze_header": "View tab → Freeze Panes → Freeze Top Row",
        "remove_duplicates": "Data tab → Remove Duplicates"
    }
}

MICROSOFT_POWERPOINT = {
    "shortcuts": {
        "new_presentation": ["ctrl", "n"],
        "open": ["ctrl", "o"],
        "save": ["ctrl", "s"],
        "save_as": ["ctrl", "shift", "s"],
        "print": ["ctrl", "p"],
        "undo": ["ctrl", "z"],
        "redo": ["ctrl", "y"],
        "copy": ["ctrl", "c"],
        "cut": ["ctrl", "x"],
        "paste": ["ctrl", "v"],
        "select_all": ["ctrl", "a"],
        "new_slide": ["ctrl", "m"],
        "duplicate_slide": ["ctrl", "d"],
        "delete_slide": ["delete"],
        "start_slideshow": ["f5"],
        "start_from_current": ["shift", "f5"],
        "end_slideshow": ["escape"],
        "next_slide": ["right"],
        "previous_slide": ["left"],
        "bold": ["ctrl", "b"],
        "italic": ["ctrl", "i"],
        "underline": ["ctrl", "u"],
        "center": ["ctrl", "e"],
        "zoom_fit": ["ctrl", "shift", "f5"],
        "group_objects": ["ctrl", "g"],
        "ungroup": ["ctrl", "shift", "g"]
    },
    "common_tasks": {
        "add_slide": "Home tab → New Slide → choose layout",
        "change_layout": "Home tab → Layout → choose layout",
        "add_image": "Insert tab → Pictures → This Device",
        "add_chart": "Insert tab → Chart → choose type",
        "add_video": "Insert tab → Video → This Device",
        "add_animation": "Animations tab → choose animation",
        "add_transition": "Transitions tab → choose transition",
        "change_theme": "Design tab → choose theme",
        "slide_master": "View tab → Slide Master",
        "export_pdf": "File → Export → Create PDF/XPS",
        "export_video": "File → Export → Create a Video",
        "presenter_view": "Slide Show tab → Use Presenter View"
    }
}

MICROSOFT_OUTLOOK = {
    "shortcuts": {
        "new_email": ["ctrl", "n"],
        "reply": ["ctrl", "r"],
        "reply_all": ["ctrl", "shift", "r"],
        "forward": ["ctrl", "f"],
        "send": ["ctrl", "enter"],
        "save_draft": ["ctrl", "s"],
        "delete": ["delete"],
        "mark_read": ["ctrl", "q"],
        "mark_unread": ["ctrl", "u"],
        "flag": ["insert"],
        "find": ["ctrl", "e"],
        "calendar": ["ctrl", "2"],
        "contacts": ["ctrl", "3"],
        "tasks": ["ctrl", "4"],
        "inbox": ["ctrl", "1"],
        "new_appointment": ["ctrl", "shift", "a"],
        "new_meeting": ["ctrl", "shift", "q"],
        "new_contact": ["ctrl", "shift", "c"]
    },
    "common_tasks": {
        "compose_email": "Click New Email → fill To, Subject, Body → Send",
        "add_attachment": "New Email → Insert tab → Attach File",
        "create_folder": "Right click Inbox → New Folder",
        "create_rule": "Home tab → Rules → Create Rule",
        "set_out_of_office": "File → Automatic Replies",
        "schedule_meeting": "Calendar → New Meeting → add attendees",
        "set_reminder": "New Appointment → Reminder dropdown",
        "search_emails": "Search box at top → type keywords",
        "sort_inbox": "Click column header to sort",
        "mark_spam": "Right click email → Junk → Block Sender"
    }
}
GOOGLE_CHROME = {
    "shortcuts": {
        "new_tab": ["ctrl", "t"],
        "close_tab": ["ctrl", "w"],
        "reopen_tab": ["ctrl", "shift", "t"],
        "new_window": ["ctrl", "n"],
        "new_incognito": ["ctrl", "shift", "n"],
        "refresh": ["f5"],
        "hard_refresh": ["ctrl", "shift", "r"],
        "address_bar": ["ctrl", "l"],
        "find": ["ctrl", "f"],
        "bookmark": ["ctrl", "d"],
        "history": ["ctrl", "h"],
        "downloads": ["ctrl", "j"],
        "extensions": ["ctrl", "shift", "e"],
        "developer_tools": ["f12"],
        "zoom_in": ["ctrl", "equal"],
        "zoom_out": ["ctrl", "minus"],
        "zoom_reset": ["ctrl", "0"],
        "next_tab": ["ctrl", "tab"],
        "previous_tab": ["ctrl", "shift", "tab"],
        "go_back": ["alt", "left"],
        "go_forward": ["alt", "right"],
        "print": ["ctrl", "p"],
        "save_page": ["ctrl", "s"],
        "view_source": ["ctrl", "u"],
        "fullscreen": ["f11"],
        "focus_first_tab": ["ctrl", "1"],
        "focus_last_tab": ["ctrl", "9"],
        "scroll_down": ["space"],
        "scroll_up": ["shift", "space"],
        "go_to_top": ["ctrl", "home"],
        "go_to_bottom": ["ctrl", "end"]
    },
    "common_tasks": {
        "open_website": "Click address bar (Ctrl+L) → type URL → Enter",
        "open_new_tab": "Press Ctrl+T → type URL in address bar",
        "search_google": "Click address bar → type search query → Enter",
        "bookmark_page": "Press Ctrl+D → click Save",
        "clear_history": "Ctrl+H → click Clear browsing data",
        "open_incognito": "Ctrl+Shift+N for private browsing",
        "download_file": "Click download link → file saves to Downloads folder",
        "open_devtools": "Press F12 to open developer tools",
        "inspect_element": "Right click element → Inspect",
        "view_page_source": "Ctrl+U to view HTML source",
        "zoom_page": "Ctrl+Plus to zoom in, Ctrl+Minus to zoom out",
        "find_on_page": "Ctrl+F → type text to find",
        "open_extensions": "Click three dots menu → More tools → Extensions",
        "manage_passwords": "Click three dots → Settings → Autofill → Passwords",
        "open_settings": "Click three dots menu → Settings"
    }
}

VSCODE = {
    "shortcuts": {
        "command_palette": ["ctrl", "shift", "p"],
        "quick_open": ["ctrl", "p"],
        "new_file": ["ctrl", "n"],
        "open_file": ["ctrl", "o"],
        "save": ["ctrl", "s"],
        "save_all": ["ctrl", "k", "s"],
        "close_file": ["ctrl", "w"],
        "undo": ["ctrl", "z"],
        "redo": ["ctrl", "shift", "z"],
        "cut": ["ctrl", "x"],
        "copy": ["ctrl", "c"],
        "paste": ["ctrl", "v"],
        "find": ["ctrl", "f"],
        "replace": ["ctrl", "h"],
        "find_in_files": ["ctrl", "shift", "f"],
        "replace_in_files": ["ctrl", "shift", "h"],
        "toggle_terminal": ["ctrl", "grave"],
        "new_terminal": ["ctrl", "shift", "grave"],
        "split_editor": ["ctrl", "backslash"],
        "toggle_sidebar": ["ctrl", "b"],
        "toggle_explorer": ["ctrl", "shift", "e"],
        "toggle_search": ["ctrl", "shift", "f"],
        "toggle_git": ["ctrl", "shift", "g"],
        "toggle_debug": ["ctrl", "shift", "d"],
        "toggle_extensions": ["ctrl", "shift", "x"],
        "go_to_line": ["ctrl", "g"],
        "go_to_definition": ["f12"],
        "peek_definition": ["alt", "f12"],
        "rename_symbol": ["f2"],
        "format_document": ["ctrl", "shift", "i"],
        "comment_line": ["ctrl", "slash"],
        "duplicate_line": ["alt", "shift", "down"],
        "delete_line": ["ctrl", "shift", "k"],
        "move_line_up": ["alt", "up"],
        "move_line_down": ["alt", "down"],
        "select_line": ["ctrl", "l"],
        "multi_cursor": ["alt", "click"],
        "select_all_occurrences": ["ctrl", "shift", "l"],
        "indent": ["tab"],
        "outdent": ["shift", "tab"],
        "fold_code": ["ctrl", "shift", "lbracket"],
        "unfold_code": ["ctrl", "shift", "rbracket"],
        "zen_mode": ["ctrl", "k", "z"],
        "run_code": ["f5"],
        "stop_code": ["shift", "f5"],
        "debug_step_over": ["f10"],
        "debug_step_into": ["f11"],
        "add_breakpoint": ["f9"],
        "open_settings": ["ctrl", "comma"],
        "keyboard_shortcuts": ["ctrl", "k", "ctrl", "s"],
        "markdown_preview": ["ctrl", "shift", "v"],
        "close_all_editors": ["ctrl", "k", "w"],
        "reopen_closed": ["ctrl", "shift", "t"]
    },
    "common_tasks": {
        "open_project": "File → Open Folder → select project folder",
        "create_new_file": "Explorer panel → hover folder → click New File icon",
        "install_extension": "Ctrl+Shift+X → search extension → click Install",
        "open_terminal": "Ctrl+` to toggle integrated terminal",
        "run_python": "Open .py file → press F5 or right click → Run Python File",
        "git_commit": "Ctrl+Shift+G → stage changes → type message → Ctrl+Enter",
        "git_push": "Source Control panel → three dots → Push",
        "format_code": "Ctrl+Shift+I to auto format document",
        "find_replace": "Ctrl+H to find and replace in current file",
        "multi_cursor_edit": "Hold Alt → click multiple locations to edit simultaneously",
        "split_screen": "Ctrl+\\ to split editor into two panels",
        "change_language": "Click language in bottom right → select language",
        "open_settings_json": "Ctrl+Shift+P → type settings json → open",
        "toggle_word_wrap": "Alt+Z to toggle word wrap",
        "go_to_symbol": "Ctrl+Shift+O to navigate to symbol in file",
        "peek_errors": "Ctrl+Shift+M to see all errors and warnings",
        "live_share": "Install Live Share extension → share session link",
        "emmet_abbreviation": "Type abbreviation → press Tab to expand HTML",
        "rename_variable": "Click variable → press F2 → type new name → Enter"
    }
}

SPOTIFY = {
    "shortcuts": {
        "play_pause": ["space"],
        "next_track": ["ctrl", "right"],
        "previous_track": ["ctrl", "left"],
        "volume_up": ["ctrl", "up"],
        "volume_down": ["ctrl", "down"],
        "mute": ["ctrl", "shift", "down"],
        "shuffle": ["ctrl", "s"],
        "repeat": ["ctrl", "r"],
        "like_song": ["alt", "shift", "b"],
        "search": ["ctrl", "l"],
        "new_playlist": ["ctrl", "n"],
        "fullscreen": ["ctrl", "shift", "f"]
    },
    "common_tasks": {
        "search_song": "Press Ctrl+L → type song name → Enter",
        "create_playlist": "Click New Playlist in sidebar → name it",
        "add_to_playlist": "Right click song → Add to playlist → select playlist",
        "download_song": "Click three dots on song → Save to your liked songs",
        "share_song": "Right click song → Share → Copy link"
    }
}

FILE_EXPLORER = {
    "shortcuts": {
        "new_folder": ["ctrl", "shift", "n"],
        "open": ["enter"],
        "rename": ["f2"],
        "delete": ["delete"],
        "permanent_delete": ["shift", "delete"],
        "copy": ["ctrl", "c"],
        "cut": ["ctrl", "x"],
        "paste": ["ctrl", "v"],
        "undo": ["ctrl", "z"],
        "select_all": ["ctrl", "a"],
        "search": ["ctrl", "f"],
        "properties": ["alt", "enter"],
        "go_up": ["alt", "up"],
        "go_back": ["alt", "left"],
        "go_forward": ["alt", "right"],
        "address_bar": ["alt", "d"],
        "new_window": ["ctrl", "n"],
        "close": ["ctrl", "w"],
        "refresh": ["f5"],
        "show_hidden": ["alt", "v", "h"],
        "preview_pane": ["alt", "p"],
        "details_pane": ["alt", "shift", "p"],
        "view_details": ["ctrl", "shift", "6"],
        "view_icons": ["ctrl", "shift", "2"],
        "view_list": ["ctrl", "shift", "1"]
    },
    "common_tasks": {
        "create_folder": "Ctrl+Shift+N → type folder name → Enter",
        "rename_file": "Click file → press F2 → type new name → Enter",
        "copy_file": "Select file → Ctrl+C → navigate to destination → Ctrl+V",
        "move_file": "Select file → Ctrl+X → navigate to destination → Ctrl+V",
        "delete_file": "Select file → Delete key → confirm",
        "search_file": "Ctrl+F → type filename",
        "show_file_path": "Click address bar (Alt+D) to see full path",
        "compress_file": "Right click file → Send to → Compressed folder",
        "extract_zip": "Right click zip → Extract All → choose destination",
        "open_as_admin": "Right click file → Run as administrator",
        "pin_to_quick_access": "Right click folder → Pin to Quick access"
    }
}
def get_app_knowledge(app: str):
    app = app.lower()
    if "word" in app:
        return MICROSOFT_WORD
    elif "excel" in app:
        return MICROSOFT_EXCEL
    elif "powerpoint" in app or "ppt" in app:
        return MICROSOFT_POWERPOINT
    elif "outlook" in app:
        return MICROSOFT_OUTLOOK
    elif "chrome" in app or "browser" in app:
        return GOOGLE_CHROME
    elif "vscode" in app or "vs code" in app or "code" in app:
        return VSCODE
    elif "spotify" in app or "music" in app:
        return SPOTIFY
    elif "explorer" in app or "files" in app or "folder" in app:
        return FILE_EXPLORER
    elif "windows" in app or "system" in app:
        return WINDOWS_SYSTEM
    else:
        return WINDOWS_SYSTEM
   

def get_shortcut(app: str, action: str):
    knowledge = get_app_knowledge(app)
    shortcuts = knowledge.get("shortcuts", {})
    return shortcuts.get(action, None)

def get_task_steps(app: str, task: str):
    knowledge = get_app_knowledge(app)
    tasks = knowledge.get("common_tasks", {})
    for key, steps in tasks.items():
        if key.lower() in task.lower() or task.lower() in key.lower():
            return steps
    return None

def format_knowledge_for_prompt(app: str):
    knowledge = get_app_knowledge(app)
    shortcuts = knowledge.get("shortcuts", {})
    tasks = knowledge.get("common_tasks", {})

    text = f"Knowledge base for {app}:\n\n"
    text += "Key shortcuts:\n"
    for action, keys in list(shortcuts.items())[:15]:
        text += f"  {action}: {'+'.join(keys)}\n"
    text += "\nCommon tasks:\n"
    for task, steps in tasks.items():
        text += f"  {task}: {steps}\n"
    return text

if __name__ == "__main__":
    print("Testing knowledge base...\n")
    print("Word save shortcut:", get_shortcut("word", "save"))
    print("Excel sum shortcut:", get_shortcut("excel", "sum"))
    print("PowerPoint new slide:", get_shortcut("powerpoint", "new_slide"))
    print()
    print("How to create chart in Excel:")
    print(get_task_steps("excel", "create_chart"))
    print()
    print(format_knowledge_for_prompt("word"))
