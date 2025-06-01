# Diagnostic print statements at the VERY BEGINNING
import sys
import os 
import uuid 
from pathlib import Path 
from datetime import datetime, timezone 
import yaml 

try:
    print("--- SCRIPT EXECUTION STARTED ---")
    import flet
    print(f"--- DIAGNOSTICS START ---")
    # ... (остальная диагностика как в твоем коде) ...
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"sys.path:")
    for p in sys.path:
        print(f"  - {p}")
    print(f"Attempting to import 'flet'...")
    print(f"Flet module loaded from: {flet.__file__}")
    print(f"Is 'icons' an attribute of the loaded flet module? {'icons' in dir(flet)}")
    print(f"Is 'Icons' an attribute of the loaded flet module? {'Icons' in dir(flet)}")
    print(f"Is 'colors' an attribute of the loaded flet module? {'colors' in dir(flet)}")
    print(f"Is 'Colors' an attribute of the loaded flet module? {'Colors' in dir(flet)}")
    print(f"--- DIAGNOSTICS END ---")
    del flet 
except ImportError as e:
    print(f"--- DIAGNOSTICS START ---")
    print(f"Failed to import flet: {e}")
    # ... (остальная диагностика) ...
    sys.exit("Could not import flet for diagnostics")


import flet as ft

# --- Управление данными заметок ---
NOTES_DIR = Path("notes_data")
NOTES_DIR.mkdir(parents=True, exist_ok=True)

class NoteData:
    def __init__(self, id, title, content, created_str, updated_str, tags, meta_type, status, responsible, file_path=None):
        self.id = id
        self.title = title
        self.content = content
        self.created_str = created_str 
        self.updated_str = updated_str
        self.tags = tags if tags else []
        self.meta_type = meta_type
        self.status = status
        self.responsible = responsible
        self.file_path: Path | None = Path(file_path) if file_path else None

    @classmethod
    def from_metadata_and_content(cls, metadata: dict, content_md: str, file_path: Path):
        note_id = metadata.get("id", file_path.stem)
        title = metadata.get("title", file_path.stem.replace('-', ' ').capitalize())
        
        created_iso = metadata.get("created", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
        updated_iso = metadata.get("updated", created_iso)

        try:
            created_dt = datetime.fromisoformat(created_iso.replace("Z", "+00:00"))
        except ValueError:
            created_dt = datetime.now(timezone.utc) 
        try:
            updated_dt = datetime.fromisoformat(updated_iso.replace("Z", "+00:00"))
        except ValueError:
            updated_dt = created_dt 

        return cls(
            id=note_id,
            title=title,
            content=content_md,
            created_str=created_dt.strftime("%d %b %Y г. %H:%M"),
            updated_str=updated_dt.strftime("%d %b %Y г. %H:%M"),
            tags=metadata.get("tags", []),
            meta_type=metadata.get("meta_type", "Заметка"),
            status=metadata.get("status", "Нет статуса"),
            responsible=metadata.get("responsible", "Не указан"),
            file_path=file_path
        )

    def to_dict_for_yaml(self):
        try:
            created_iso = datetime.strptime(self.created_str, "%d %b %Y г. %H:%M").replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError: 
            created_iso = self.created_str if 'T' in self.created_str else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        updated_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        return {
            "id": self.id,
            "title": self.title,
            "created": created_iso,
            "updated": updated_iso,
            "tags": self.tags,
            "meta_type": self.meta_type,
            "status": self.status,
            "responsible": self.responsible,
        }

def parse_front_matter(md_content: str):
    try:
        if md_content.startswith("---"):
            parts = md_content.split("---", 2)
            if len(parts) >= 3:
                front_matter_str = parts[1]
                content_md = parts[2].lstrip()
                metadata = yaml.safe_load(front_matter_str)
                return metadata, content_md
    except Exception as e:
        print(f"Error parsing front matter: {e}")
    return {}, md_content


def load_note_from_file(file_path: Path) -> NoteData | None:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            full_content = f.read()
        metadata, content_md = parse_front_matter(full_content)
        if not metadata: 
            metadata = {"id": file_path.stem, "title": file_path.stem.replace('-', ' ').capitalize()}

        return NoteData.from_metadata_and_content(metadata, content_md, file_path)
    except Exception as e:
        print(f"Error loading note from {file_path}: {e}")
        return None

def load_all_notes_from_disk() -> dict[str, NoteData]:
    notes = {}
    for file_path in NOTES_DIR.glob("*.md"):
        note_data = load_note_from_file(file_path)
        if note_data:
            notes[note_data.id] = note_data
    return notes

def save_note_to_disk(note_data: NoteData):
    metadata_to_save = note_data.to_dict_for_yaml()
    note_data.updated_str = datetime.fromisoformat(metadata_to_save["updated"].replace("Z", "+00:00")).strftime("%d %b %Y г. %H:%M")

    front_matter_str = yaml.dump(metadata_to_save, sort_keys=False, allow_unicode=True, indent=2)
    file_content = f"---\n{front_matter_str}---\n\n{note_data.content}"
    
    if not note_data.file_path: 
        note_data.file_path = NOTES_DIR / f"{note_data.id}.md"

    try:
        with open(note_data.file_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        print(f"Note '{note_data.title}' saved to {note_data.file_path}")
    except Exception as e:
        print(f"Error saving note {note_data.title} to {note_data.file_path}: {e}")

def create_new_draft_note() -> NoteData:
    new_id = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)
    now_str = now_utc.strftime("%d %b %Y г. %H:%M")
    
    file_path = NOTES_DIR / f"{new_id}.md"

    return NoteData(
        id=new_id,
        title="Новая заметка",
        content="",
        created_str=now_str,
        updated_str=now_str,
        tags=[],
        meta_type="Заметка",
        status="Черновик",
        responsible="",
        file_path=file_path 
    )

def delete_note_from_disk(note_id: str, notes_collection: dict) -> bool:
    if note_id in notes_collection:
        note_to_delete = notes_collection[note_id]
        if note_to_delete.file_path and note_to_delete.file_path.exists():
            try:
                note_to_delete.file_path.unlink() 
                print(f"Deleted file: {note_to_delete.file_path}")
            except Exception as e:
                print(f"Error deleting file {note_to_delete.file_path}: {e}")
                return False 
        del notes_collection[note_id] 
        return True
    return False
# --- Конец управления данными ---

ALL_NOTES_DICT: dict[str, NoteData] = {}
ALL_GLOBAL_TAGS_LIST = []

class NovaMindApp:
    # ... (__init__, _update_all_tags_list_from_notes, build_appbar, build_left_rail, 
    #      _update_menu_selection, handle_menu_click, filter_by_tag, show_view,
    #      display_empty_state, display_note, display_note_details, display_placeholder_view,
    #      go_to_new_note_editor, edit_note_clicked - все как в предыдущем полном коде)

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "NovaMind"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        
        global ALL_NOTES_DICT 
        ALL_NOTES_DICT = load_all_notes_from_disk()
        self._update_all_tags_list_from_notes()

        self.current_note_id: str | None = None 
        self.current_editing_note_data: NoteData | None = None 
        self.menu_list_tiles = [] 
        self.selected_menu_item_index = 1 

        self.left_rail_content_column = self.build_left_rail() 
        self.left_rail_content_container = ft.Container(
            content=self.left_rail_content_column,
            width=220, 
        )
        
        self.main_content_area = ft.Column(expand=True, spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
        self.right_details_pane = ft.Container(
            content=ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10), 
            width=300,
            padding=ft.padding.all(15),
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
            visible=False
        )
        self.page.appbar = self.build_appbar()
        self.page.add(
            ft.Row(
                [
                    self.left_rail_content_container, 
                    ft.VerticalDivider(width=1),
                    ft.Container(self.main_content_area, expand=True, padding=20),
                    ft.VerticalDivider(width=1),
                    self.right_details_pane
                ],
                expand=True, 
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        )
        
        if self.selected_menu_item_index == 1: 
            if ALL_NOTES_DICT:
                first_note_id = sorted(list(ALL_NOTES_DICT.keys()))[0] if ALL_NOTES_DICT else None
                self.current_note_id = first_note_id
        else: 
             self.current_note_id = f"placeholder_view_{self.selected_menu_item_index}"
        
        self.show_view()
        self._update_menu_selection()

    def _update_all_tags_list_from_notes(self):
        global ALL_GLOBAL_TAGS_LIST, ALL_NOTES_DICT
        seen_tags = set()
        for note in ALL_NOTES_DICT.values():
            for tag in note.tags:
                seen_tags.add(tag)
        ALL_GLOBAL_TAGS_LIST = sorted(list(seen_tags))

    def build_appbar(self):
        return ft.AppBar(
            leading=ft.Text("NovaMind", weight=ft.FontWeight.BOLD, size=16),
            leading_width=300,
            actions=[
                ft.IconButton(ft.Icons.SEARCH_ROUNDED, tooltip="Поиск"),
                ft.Container(padding=ft.padding.only(right=10)),
                ft.Stack(
                    [
                        ft.CircleAvatar(bgcolor=ft.Colors.BLUE_GREY_700, radius=18),
                        ft.Text("КД", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.WHITE),
                    ],
                    alignment=ft.alignment.center
                ),
                ft.Container(padding=ft.padding.only(right=10)),
            ],
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        )

    def build_left_rail(self):
        self.menu_list_tiles.clear() 

        main_menu_items_data = [
            {"label": "Проекты", "icon": ft.Icons.FOLDER_OUTLINED, "index": 0},
            {"label": "Заметки", "icon": ft.Icons.DESCRIPTION_OUTLINED, "index": 1},
            {"label": "Граф", "icon": ft.Icons.SHARE_OUTLINED, "index": 2},
        ]
        
        quick_access_items_data = [
            {"label": "Ключевой проект", "icon": ft.Icons.KEY_OUTLINED, "index": 3},
            {"label": "Ежедневник", "icon": ft.Icons.CALENDAR_TODAY_OUTLINED, "index": 4},
        ]

        for item_def in main_menu_items_data:
            tile = ft.ListTile(
                title=ft.Text(item_def["label"]), 
                leading=ft.Icon(item_def["icon"]), 
                dense=True, 
                on_click=lambda e, idx=item_def["index"], name=item_def["label"]: self.handle_menu_click(name, idx), 
                data=item_def["index"]
            )
            self.menu_list_tiles.append(tile)
        
        self.menu_list_tiles.append(ft.Divider(height=10)) 

        for item_def in quick_access_items_data:
            tile = ft.ListTile(
                title=ft.Text(item_def["label"]), 
                leading=ft.Icon(item_def["icon"]), 
                dense=True, 
                on_click=lambda e, idx=item_def["index"], name=item_def["label"]: self.handle_menu_click(name, idx), 
                data=item_def["index"]
            )
            self.menu_list_tiles.append(tile)

        tag_controls_list = [] 
        global ALL_GLOBAL_TAGS_LIST 
        if ALL_GLOBAL_TAGS_LIST:
            for tag_text in ALL_GLOBAL_TAGS_LIST:
                 tag_controls_list.append(
                    ft.Container( 
                        content=ft.TextButton(
                            content=ft.Text(tag_text, color=ft.Colors.SECONDARY, size=13),
                            on_click=lambda e, t=tag_text: self.filter_by_tag(t),
                            style=ft.ButtonStyle(padding=ft.padding.symmetric(vertical=1, horizontal=0))
                        ),
                        padding=ft.padding.only(left=15) 
                    )
                )
        else:
            tag_controls_list.append(
                 ft.Container(
                    content=ft.Text("Тегов пока нет", italic=True, color=ft.Colors.OUTLINE),
                    padding=ft.padding.only(left=15)
                 )
            )
        
        tags_section = ft.Column(
            [
                ft.Container(
                    content=ft.Text("ТЕГИ", weight=ft.FontWeight.BOLD, color=ft.Colors.OUTLINE, size=12),
                    margin=ft.margin.only(left=15, top=10, bottom=5) 
                ),
                ft.Column(tag_controls_list, spacing=0, scroll=ft.ScrollMode.ADAPTIVE)
            ]
        )

        return ft.Column( 
            [
                ft.Container( 
                    content=ft.Text("МЕНЮ", weight=ft.FontWeight.BOLD, color=ft.Colors.OUTLINE, size=12),
                    margin=ft.margin.only(top=10, left=15, bottom=5)
                ),
                ft.Column(self.menu_list_tiles, spacing=0),
                
                ft.Container(expand=True), 
                
                ft.Divider(height=1), 
                tags_section, 
            ],
            expand=True, 
            scroll=ft.ScrollMode.ADAPTIVE 
        )

    def _update_menu_selection(self):
        for tile in self.menu_list_tiles:
            if isinstance(tile, ft.ListTile): 
                if isinstance(tile.data, int) and tile.data == self.selected_menu_item_index:
                    tile.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY)
                else:
                    tile.bgcolor = None 
        if self.page: 
            try:
                self.page.update()
            except Exception as e:
                print(f"Error updating page in _update_menu_selection: {e}")

    def handle_menu_click(self, item_name: str, item_index: int, initial_load=False):
        global ALL_NOTES_DICT
        print(f"Menu item clicked: {item_name}, index: {item_index}")
        self.selected_menu_item_index = item_index
        self.current_editing_note_data = None 

        if item_index == 1: 
            if ALL_NOTES_DICT:
                sorted_note_ids = sorted(list(ALL_NOTES_DICT.keys()))
                self.current_note_id = sorted_note_ids[0] if sorted_note_ids else None
            else:
                self.current_note_id = None 
        elif item_index in [0, 2, 3, 4]: 
            self.current_note_id = f"placeholder_view_{item_index}"
        else: 
            self.current_note_id = f"placeholder_view_{item_index}"

        if not initial_load:
            self.show_view()
            self._update_menu_selection() 
            self.page.update()
        elif self.current_note_id or item_index == 1:
             self.show_view()


    def filter_by_tag(self, tag_name):
        print(f"Filter by tag: {tag_name}")
        self.selected_menu_item_index = -1 
        self._update_menu_selection()
        self.main_content_area.controls.clear()
        self.main_content_area.controls.append(ft.Text(f"Фильтр по тегу: {tag_name}", size=20))
        self.page.update()


    def show_view(self):
        global ALL_NOTES_DICT
        self.main_content_area.controls.clear()
        self.right_details_pane.visible = False
        if self.right_details_pane.content:
             self.right_details_pane.content.controls.clear()

        if self.current_editing_note_data:
            self.display_note_editor(self.current_editing_note_data)
            self.right_details_pane.visible = False
        elif self.current_note_id and self.current_note_id in ALL_NOTES_DICT:
            note = ALL_NOTES_DICT[self.current_note_id]
            self.display_note(note) 
            self.display_note_details(note) 
            self.right_details_pane.visible = True
        elif self.current_note_id and self.current_note_id.startswith("placeholder_view_"):
            self.display_placeholder_view(self.current_note_id)
        else: 
            self.display_empty_state()
    
    def display_empty_state(self):
        self.main_content_area.controls.extend([
            ft.Container(height=50),
            ft.Icon(ft.Icons.NOTE_ADD_OUTLINED, size=60, color=ft.Colors.OUTLINE),
            ft.Text("NovaMind: Ваш новый центр идей", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Готовы зафиксировать первую мысль, составить план или начать исследование?\n"
                "Просто создайте свою первую заметку.",
                size=16, color=ft.Colors.OUTLINE, text_align=ft.TextAlign.CENTER, width=500
            ),
            ft.Container(height=10),
            ft.ElevatedButton(
                icon=ft.Icons.ADD,
                text="Создать первую заметку",
                on_click=self.go_to_new_note_editor, 
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.TEAL_ACCENT_700,
                    color=ft.Colors.WHITE,
                    padding=ft.padding.symmetric(vertical=15, horizontal=25)
                )
            ),
            ft.Container(height=30),
            ft.Text("Несколько идей для начала:", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.OUTLINE),
            ft.Column([
                ft.Text("• Список дел на сегодня", color=ft.Colors.OUTLINE),
                ft.Text("• Идеи для нового проекта", color=ft.Colors.OUTLINE),
                ft.Text("• Конспект интересной статьи", color=ft.Colors.OUTLINE),
                ft.Text("• Просто свободные мысли", color=ft.Colors.OUTLINE),
            ], spacing=5, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.START)
        ])
        self.main_content_area.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.main_content_area.alignment = ft.MainAxisAlignment.START

    def display_note(self, note: NoteData):
        tag_chips = [
            ft.Chip(
                label=ft.Text(tag, color=ft.Colors.TEAL_ACCENT_200),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.TEAL_ACCENT_200),
            ) for tag in note.tags
        ]
        
        edit_button = ft.IconButton(ft.Icons.EDIT, tooltip="Редактировать", on_click=lambda e, n=note: self.edit_note_clicked(n))
        delete_button = ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Удалить", 
                                      on_click=lambda e, note_id=note.id: self.confirm_delete_note(note_id), 
                                      icon_color=ft.Colors.RED_ACCENT_200)

        self.main_content_area.controls.extend([
            ft.Row([
                ft.Text(note.title, size=32, weight=ft.FontWeight.BOLD, expand=True),
                edit_button,
                delete_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([
                ft.Text(f"Создано: {note.created_str}", size=12, color=ft.Colors.OUTLINE),
                ft.Text(f"Обновлено: {note.updated_str}", size=12, color=ft.Colors.OUTLINE),
            ], spacing=20),
            ft.Row(tag_chips, spacing=5, wrap=True),
            ft.Divider(),
            ft.Markdown(note.content if note.content else "*Нет содержимого*", 
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, 
                        code_theme="atom-one-dark",
                        expand=True),
        ])
        self.main_content_area.horizontal_alignment = ft.CrossAxisAlignment.START
        self.main_content_area.alignment = ft.MainAxisAlignment.START

    def display_note_details(self, note: NoteData):
        def create_link_list(title, links_data): 
            link_items = [ft.Text(title, weight=ft.FontWeight.BOLD, color=ft.Colors.OUTLINE, size=12)]
            link_items.append(ft.Text("Пока не реализовано", italic=True, color=ft.Colors.OUTLINE, size=12))
            return ft.Column(link_items, spacing=2)

        if not self.right_details_pane.content: 
            self.right_details_pane.content = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
        
        self.right_details_pane.content.controls.extend([
            ft.Text("ИНФОРМАЦИЯ О СТРАНИЦЕ", weight=ft.FontWeight.BOLD, color=ft.Colors.OUTLINE, size=12),
            ft.Row([ft.Text("Тип:", color=ft.Colors.OUTLINE, size=13), ft.Text(note.meta_type, size=13)]),
            ft.Row([ft.Text("Статус:", color=ft.Colors.OUTLINE, size=13), ft.Text(note.status, size=13)]),
            ft.Row([ft.Text("Ответственный:", color=ft.Colors.OUTLINE, size=13), ft.Text(note.responsible, size=13)]),
            ft.Divider(height=20),
            create_link_list("СОДЕРЖАНИЕ", []), 
            ft.Divider(height=20),
            create_link_list("ОБРАТНЫЕ ССЫЛКИ (BACKLINKS)", []),
            ft.Divider(height=20),
            create_link_list("ИСХОДЯЩИЕ ССЫЛКИ", []),
        ])
        self.right_details_pane.content.controls.append(ft.Container(expand=True))
        self.right_details_pane.content.controls.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.OUTLINE, size=18),
                    ft.Text("Выберите заметку, чтобы увидеть\nздесь ее детали, содержание и связи.",
                            color=ft.Colors.OUTLINE, size=11, max_lines=2)
                ],
                spacing=8, alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    def display_placeholder_view(self, view_id):
        view_name_parts = view_id.split("_")
        selected_idx_str = view_name_parts[-1] if len(view_name_parts) > 0 else ""
        
        label = "Неизвестный раздел"
        try:
            idx = int(selected_idx_str)
            if idx == 0: label = "Проекты"
            elif idx == 1: label = "Заметки" 
            elif idx == 2: label = "Граф"
            elif idx == 3: label = "Ключевой проект" 
            elif idx == 4: label = "Ежедневник"    
        except ValueError:
            print(f"Ошибка преобразования индекса '{selected_idx_str}' в int в display_placeholder_view (из view_id: {view_id})")
        
        self.main_content_area.controls.append(
            ft.Column([
                ft.Icon(ft.Icons.CONSTRUCTION, size=50, color=ft.Colors.OUTLINE),
                ft.Text(f"Раздел '{label}' в разработке", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Содержимое для этого раздела скоро появится.", color=ft.Colors.OUTLINE)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER, expand=True, spacing=10)
        )
        self.main_content_area.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.main_content_area.alignment = ft.MainAxisAlignment.CENTER

    def go_to_new_note_editor(self, e): 
        print("Переход в режим создания новой заметки")
        self.current_editing_note_data = create_new_draft_note()
        self.current_note_id = None 
        self.selected_menu_item_index = -1 
        self._update_menu_selection()
        self.show_view() 
        self.page.update()

    def edit_note_clicked(self, note_data: NoteData):
        print(f"Редактирование заметки: {note_data.title}")
        self.current_editing_note_data = note_data 
        self.current_note_id = None 
        self.selected_menu_item_index = -1 
        self._update_menu_selection()
        self.show_view() 
        self.page.update()

    def display_note_editor(self, note_to_edit: NoteData): # ИЗМЕНЕННЫЙ МЕТОД
        self.main_content_area.controls.clear()
        is_new_note = not (note_to_edit.id in ALL_NOTES_DICT)

        title_field = ft.TextField(label="Заголовок", value=note_to_edit.title, autofocus=True, border_color=ft.Colors.OUTLINE)
        content_field = ft.TextField(label="Содержимое (Markdown)", value=note_to_edit.content, 
                                     multiline=True, min_lines=10, max_lines=30, expand=True, border_color=ft.Colors.OUTLINE)
        tags_field = ft.TextField(label="Теги (через запятую)", value=", ".join(note_to_edit.tags), border_color=ft.Colors.OUTLINE)
        
        meta_type_field = ft.TextField(label="Тип", value=note_to_edit.meta_type, border_color=ft.Colors.OUTLINE)
        status_field = ft.TextField(label="Статус", value=note_to_edit.status, border_color=ft.Colors.OUTLINE)
        responsible_field = ft.TextField(label="Ответственный", value=note_to_edit.responsible, border_color=ft.Colors.OUTLINE)

        def save_edited_note(e):
            global ALL_NOTES_DICT 
            note_to_edit.title = title_field.value or "Без заголовка"
            note_to_edit.content = content_field.value
            note_to_edit.tags = sorted(list(set([tag.strip() for tag in tags_field.value.split(",") if tag.strip()]))) 
            note_to_edit.meta_type = meta_type_field.value
            note_to_edit.status = status_field.value
            note_to_edit.responsible = responsible_field.value
            
            save_note_to_disk(note_to_edit)
            
            ALL_NOTES_DICT[note_to_edit.id] = note_to_edit 
            self.current_editing_note_data = None 
            self.current_note_id = note_to_edit.id 
            
            self._update_all_tags_list_from_notes() 
            self._update_all_tags_list_ui()  
            
            self.selected_menu_item_index = 1 
            self._update_menu_selection()
            self.show_view() 
            self.page.update()

        def cancel_edit(e):
            self.current_editing_note_data = None
            if note_to_edit.id in ALL_NOTES_DICT and not is_new_note : 
                self.current_note_id = note_to_edit.id
            else: 
                if ALL_NOTES_DICT:
                    sorted_ids = sorted(list(ALL_NOTES_DICT.keys()))
                    self.current_note_id = sorted_ids[0] if sorted_ids else None
                else:
                    self.current_note_id = None

            self.selected_menu_item_index = 1 
            if not self.current_note_id and not ALL_NOTES_DICT: 
                pass 
            
            self._update_menu_selection()
            self.show_view()
            self.page.update()

        self.main_content_area.controls.extend([
            ft.Text("Редактирование заметки" if not is_new_note else "Создание новой заметки", size=24, weight=ft.FontWeight.BOLD),
            title_field,
            tags_field,
            meta_type_field,
            status_field,
            responsible_field,
            ft.Container( # Обертка для Text "Содержимое:"
                content=ft.Text("Содержимое:", weight=ft.FontWeight.BOLD), 
                margin=ft.margin.only(top=10)
            ),
            content_field,
            ft.Container( # Обертка для Row с кнопками
                content=ft.Row([
                    ft.ElevatedButton("Сохранить", icon=ft.Icons.SAVE, on_click=save_edited_note, bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE),
                    ft.OutlinedButton("Отмена", icon=ft.Icons.CANCEL_OUTLINED, on_click=cancel_edit) # Исправленная иконка
                ], alignment=ft.MainAxisAlignment.END, spacing=10),
                margin=ft.margin.only(top=10)
            )
        ])
        self.main_content_area.horizontal_alignment = ft.CrossAxisAlignment.STRETCH


    def confirm_delete_note(self, note_id_to_delete: str):
        # ... (как в предыдущем полном коде)
        global ALL_NOTES_DICT
        if not (note_id_to_delete in ALL_NOTES_DICT):
            return

        note_title = ALL_NOTES_DICT[note_id_to_delete].title

        def on_delete_confirm(e):
            global ALL_NOTES_DICT
            if delete_note_from_disk(note_id_to_delete, ALL_NOTES_DICT):
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Заметка '{note_title}' удалена."), open=True))
                self.current_note_id = None 
                if ALL_NOTES_DICT:
                     sorted_ids = sorted(list(ALL_NOTES_DICT.keys()))
                     self.current_note_id = sorted_ids[0] if sorted_ids else None
                else: 
                    self.current_note_id = None
                
                self._update_all_tags_list_from_notes()
                self._update_all_tags_list_ui()
                self.selected_menu_item_index = 1 
                self._update_menu_selection()
                self.show_view()
            else:
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Ошибка удаления заметки '{note_title}'."), open=True))
            close_dialog(e)

        def close_dialog(e):
            if self.page.dialog: 
                self.page.dialog.open = False
            self.page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Подтверждение удаления"),
            content=ft.Text(f"Вы уверены, что хотите удалить заметку \"{note_title}\"?\nЭто действие необратимо."),
            actions=[
                ft.TextButton("Удалить", on_click=on_delete_confirm, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ft.FilledButton("Отмена", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = confirm_dialog
        self.page.dialog.open = True
        self.page.update()
        
    def _update_all_tags_list_ui(self):
        # ... (как в предыдущем полном коде)
        old_selected_menu_index = self.selected_menu_item_index
        
        new_left_panel_column = self.build_left_rail()
        self.left_rail_content_container.content = new_left_panel_column
        
        self.selected_menu_item_index = old_selected_menu_index 
        self._update_menu_selection() 


    def navigate_to_link(self, target_note_id, anchor):
        # ... (как в предыдущем полном коде)
        global ALL_NOTES_DICT
        if target_note_id and target_note_id in ALL_NOTES_DICT:
            self.current_note_id = target_note_id
            self.show_view()
            print(f"Переход к заметке {target_note_id}, якорь: {anchor}")
        elif anchor:
             print(f"Прокрутка к якорю: {anchor} в текущей заметке")
        else:
            print(f"Не удалось перейти: {target_note_id}, {anchor}")
        self.page.update()


def main(page: ft.Page):
    app = NovaMindApp(page)

ft.app(target=main)