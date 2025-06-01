**NovaMind** is a knowledge management and note-taking desktop application inspired by **Obsidian** and **Notion**, built in pure **Python** using **Flet**, a cross-platform UI framework based on Flutter.

# NovaMind Philosophy
- **Markdown as a basis.** All notes are regular `.md` files with front matter in YAML.
- **Local storage.** You own your data. All files are on disk, no clouds.
- **Flexible structure.** Tag navigation, sidebars, quick switching between sections.
- **Block system.** Inside a note, everything is blocks: headings, tags, metadata, markdown.
- **Minimalism + power.** Clean interface, no distracting elements. Only the idea and its form.

# Key features
1. **Navigation**
- Sidebar with menu: **Projects**, **Notes**, **Schedule**, **Diary**.
- Separate list of pinned sections.
- All tags section: click — and you will see the filter.
2. **Notes**
- Create, edit, delete.
- Each note: `.md` file with YAML metainformation.
- Editor with fields: `Title`, `Tags`, `Type`, `Status`, `Responsible`, `Markdown`.
- Markdown view support with code highlighting.
3. **Tags and filtering**
- Global tag list.
- Filter notes by tag with one button.
4. **Block Structure**
- Separate content and metadata.
- Content is markdown, meta is YAML.
- Ready to extend: support for databases, table properties, and custom blocks.
5. **Note Details**
- Display details in the right panel.
- Type, status, owner.
- Coming soon: backlinks, outbound links, content.
6. **User Experience**
- Dark theme support.
- Simple, clean, responsive interface.
- Smooth interactions and visual readability.

# **Future plan**

| Category | Plans |
| ----------------- | ---------------------------------------------------- |
| 🔍 Search | Fast local search (e.g. with Whoosh/Lunr) |
| 🔗 Backlinks | Backlinks and outlinks support |
| 🧠 Relationship graph | Notes graph, relationship visualization |
| 🎛 WYSIWYG | Visual editor mode with Markdown sync |
| 🔌 Plugins | API for community extensions |
| 🧩 Block system | `/`-insert, drag-n-drop blocks, typing |

# Unresolved issues at the moment
- Fix creating/editing/deleting notes. Currently, you can only create one note, it cannot be deleted, and you cannot create another note at the same time
- Fix top bar
- Fix search
- Finish the additional panel while in a note
- Change/Fix menu panel

# Install and Run
```
pip install flet pyyaml
python main.py
```

