import reflex as rx

import logging
from typing import Any, TypedDict
from faker import Faker
from sqlalchemy import bindparam, text


class LabelData(TypedDict):
    id: int
    name: str


class ItemData(TypedDict):
    content: str
    done: bool


class NoteData(TypedDict):
    id: int
    title: str
    body: str
    color: str
    pinned: bool
    archived: bool
    trashed: bool
    checklist: bool
    items: list[ItemData]
    total: int
    completed: int
    labels: list[str]
    updated: str


class NotesState(rx.State):
    notes: list[NoteData] = []
    labels: list[LabelData] = []
    section: str = "Notes"
    archive_route: bool = False
    search: str = ""
    label_filter: int = 0
    color_filter: str = "all"
    colors: list[str] = ["paper", "butter", "sage", "peach", "rose", "sky"]
    grid: bool = True
    mobile_open: bool = False
    composer_open: bool = False
    checklist_mode: bool = False
    draft_color: str = "butter"
    draft_label: int = 0
    form_version: int = 0
    error: str = ""
    load_error: str = ""
    loading: bool = True
    saving: bool = False
    pending_delete: int = 0
    page: int = 0
    has_more: bool = False

    @rx.var
    def pinned_notes(self) -> list[NoteData]:
        return [note for note in self.notes if note["pinned"]]

    @rx.var
    def recent_notes(self) -> list[NoteData]:
        return [note for note in self.notes if not note["pinned"]]

    @rx.var
    def filtered(self) -> bool:
        return bool(
            self.search or self.label_filter or self.color_filter != "all"
        )

    @rx.event
    def load_workspace(self):
        self.archive_route = False
        if self.section == "Archive":
            self.section = "Notes"
            self.search = ""
            self.label_filter = 0
            self.color_filter = "all"
            self.page = 0
        return NotesState.load

    @rx.event
    def load_archive(self):
        self.archive_route = True
        self.section = "Archive"
        self.search = ""
        self.label_filter = 0
        self.color_filter = "all"
        self.page = 0
        self.mobile_open = False
        self.composer_open = False
        return NotesState.load

    @rx.event
    async def load(self):
        self.loading = True
        self.load_error = ""
        try:
            async with rx.asession() as session:
                # Serialize the empty-database check so concurrent first visits cannot duplicate seeds.
                await session.execute(
                    text("LOCK TABLE notes, labels IN SHARE ROW EXCLUSIVE MODE")
                )
                empty = (
                    await session.execute(
                        text(
                            "SELECT NOT EXISTS (SELECT 1 FROM notes) AND NOT EXISTS (SELECT 1 FROM labels)"
                        )
                    )
                ).scalar_one()
                if empty:
                    fake = Faker()
                    fake.seed_instance(24)
                    label_ids = []
                    for position, name in enumerate(
                        ["Personal", "Work", "Ideas"]
                    ):
                        label_ids.append(
                            (
                                await session.execute(
                                    text(
                                        "INSERT INTO labels (name, sort_order) VALUES (:name, :position) RETURNING id"
                                    ),
                                    {"name": name, "position": position},
                                )
                            ).scalar_one()
                        )
                    themes = [
                        (
                            "A little room to think",
                            "Collect the thoughts you don't want to lose. A good sentence, a small plan, a wildly impractical idea. It all belongs here.",
                            "butter",
                            False,
                        ),
                        (
                            "A slower kind of weekend",
                            "Visit the flower market\nPick up fresh sourdough\nTake the long way home\nMake something just for fun",
                            "sage",
                            True,
                        ),
                        (
                            "Less, but better",
                            "What if the next version wasn't about adding more?\n\nLeave a little breathing room. Make the important things feel effortless. Start with the simplest possible idea.",
                            "peach",
                            False,
                        ),
                        (
                            "For the next chapter",
                            "A small reading list for quiet afternoons.\n\nThe Creative Act — Rick Rubin\nA Field Guide to Getting Lost — Rebecca Solnit\nFour Thousand Weeks — Oliver Burkeman",
                            "paper",
                            False,
                        ),
                        (
                            "Little things worth keeping",
                            "The light through the kitchen window. A conversation that ran longer than expected. That feeling after finishing something difficult.\n\nPay attention to what feels like enough.",
                            "rose",
                            False,
                        ),
                        (
                            "Before we launch",
                            "Review the first draft\nCollect feedback from the team\nSimplify the welcome flow\nCheck the mobile experience\nCelebrate the small wins",
                            "sky",
                            True,
                        ),
                        (
                            "Somewhere new",
                            "A notebook, comfortable shoes, and no overly ambitious itinerary.\n\nFind a neighborhood café. Wander through a bookshop. Leave the afternoon unplanned.",
                            "sage",
                            False,
                        ),
                        (
                            "An idea for another day",
                            "A tiny collection of everyday rituals: a morning walk, a handwritten letter, a recipe passed between friends.\n\nNot everything needs to become a project.",
                            "butter",
                            False,
                        ),
                    ]
                    for position, (title, body, color, checklist) in enumerate(
                        themes
                    ):
                        if position == 2:
                            body = f"Conversation with {fake.first_name()}:\n\n{body}"
                        note_id = (
                            await session.execute(
                                text(
                                    "INSERT INTO notes (title, plain_text_content, content_format, note_type, color, is_pinned, sort_order) VALUES (:title, :body, 'plain', :kind, :color, :pinned, :position) RETURNING id"
                                ),
                                {
                                    "title": title,
                                    "body": body,
                                    "kind": "checklist"
                                    if checklist
                                    else "text",
                                    "color": color,
                                    "pinned": position < 2,
                                    "position": position,
                                },
                            )
                        ).scalar_one()
                        await session.execute(
                            text(
                                "INSERT INTO note_labels (note_id, label_id) VALUES (:note, :label)"
                            ),
                            {"note": note_id, "label": label_ids[position % 3]},
                        )
                        if checklist:
                            await session.execute(
                                text(
                                    "INSERT INTO checklist_items (note_id, content, is_completed, sort_order) VALUES (:note, :content, :done, :position)"
                                ),
                                [
                                    {
                                        "note": note_id,
                                        "content": line,
                                        "done": i == 0,
                                        "position": i,
                                    }
                                    for i, line in enumerate(body.splitlines())
                                ],
                            )
                await session.commit()
                rows = (
                    (
                        await session.execute(
                            text(
                                "SELECT id, name FROM labels ORDER BY sort_order, name LIMIT 500"
                            )
                        )
                    )
                    .mappings()
                    .all()
                )
                self.labels = [
                    {"id": int(row["id"]), "name": str(row["name"])}
                    for row in rows
                ]
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.load_error = (
                "Your workspace couldn't be loaded. Please try again."
            )
            self.loading = False
            return
        yield NotesState.refresh

    @rx.event
    async def refresh(self):
        self.loading = True
        self.load_error = ""
        yield
        try:
            async with rx.asession() as session:
                rows = (
                    (
                        await session.execute(
                            text("""
                    SELECT n.id, n.title, LEFT(n.plain_text_content, 650) AS body,
                           n.color, n.is_pinned, n.is_archived, n.is_trashed,
                           n.note_type, n.updated_at,
                           (SELECT COUNT(*) FROM checklist_items c WHERE c.note_id=n.id) AS total,
                           (SELECT COUNT(*) FROM checklist_items c WHERE c.note_id=n.id AND c.is_completed) AS completed
                    FROM notes n
                    WHERE ((:section='Trash' AND n.is_trashed)
                        OR (:section='Archive' AND n.is_archived AND NOT n.is_trashed)
                        OR (:section='Notes' AND NOT n.is_archived AND NOT n.is_trashed)
                        OR (:section='Pinned' AND n.is_pinned AND NOT n.is_archived AND NOT n.is_trashed))
                      AND (:color='all' OR n.color=:color)
                      AND (:label=0 OR EXISTS (SELECT 1 FROM note_labels nl WHERE nl.note_id=n.id AND nl.label_id=:label))
                      AND (:query='' OR POSITION(LOWER(:query) IN LOWER(n.title))>0
                        OR POSITION(LOWER(:query) IN LOWER(n.plain_text_content))>0
                        OR EXISTS (SELECT 1 FROM checklist_items ci WHERE ci.note_id=n.id AND POSITION(LOWER(:query) IN LOWER(ci.content))>0)
                        OR EXISTS (SELECT 1 FROM note_labels nl JOIN labels l ON l.id=nl.label_id WHERE nl.note_id=n.id AND POSITION(LOWER(:query) IN LOWER(l.name))>0))
                    ORDER BY n.is_pinned DESC, n.updated_at DESC, n.id DESC
                    LIMIT 49 OFFSET :offset
                """),
                            {
                                "section": self.section,
                                "color": self.color_filter,
                                "label": self.label_filter,
                                "query": self.search.strip(),
                                "offset": self.page * 48,
                            },
                        )
                    )
                    .mappings()
                    .all()
                )
                self.has_more = len(rows) > 48
                rows = rows[:48]
                ids = [int(row["id"]) for row in rows]
                item_map: dict[int, list[ItemData]] = {}
                label_map: dict[int, list[str]] = {}
                if ids:
                    items = (
                        (
                            await session.execute(
                                text(
                                    "SELECT note_id, content, is_completed FROM (SELECT note_id, content, is_completed, sort_order, id, ROW_NUMBER() OVER (PARTITION BY note_id ORDER BY sort_order, id) AS rank FROM checklist_items WHERE note_id IN :ids) ranked WHERE rank<=5 ORDER BY note_id, sort_order, id"
                                ).bindparams(bindparam("ids", expanding=True)),
                                {"ids": ids},
                            )
                        )
                        .mappings()
                        .all()
                    )
                    links = (
                        (
                            await session.execute(
                                text(
                                    "SELECT nl.note_id, l.name FROM note_labels nl JOIN labels l ON l.id=nl.label_id WHERE nl.note_id IN :ids ORDER BY nl.sort_order, l.name"
                                ).bindparams(bindparam("ids", expanding=True)),
                                {"ids": ids},
                            )
                        )
                        .mappings()
                        .all()
                    )
                    for item in items:
                        item_map.setdefault(int(item["note_id"]), []).append(
                            {
                                "content": str(item["content"]),
                                "done": bool(item["is_completed"]),
                            }
                        )
                    for link in links:
                        label_map.setdefault(int(link["note_id"]), []).append(
                            str(link["name"])
                        )
                self.notes = [
                    {
                        "id": int(row["id"]),
                        "title": str(row["title"] or "Untitled thought"),
                        "body": str(row["body"]),
                        "color": str(row["color"]),
                        "pinned": bool(row["is_pinned"]),
                        "archived": bool(row["is_archived"]),
                        "trashed": bool(row["is_trashed"]),
                        "checklist": row["note_type"] == "checklist",
                        "items": item_map.get(int(row["id"]), []),
                        "total": int(row["total"] or 0),
                        "completed": int(row["completed"] or 0),
                        "labels": label_map.get(int(row["id"]), []),
                        "updated": row["updated_at"].strftime("%b %d, %Y"),
                    }
                    for row in rows
                ]
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.load_error = (
                "We couldn't refresh your notes. Try again in a moment."
            )
        finally:
            self.loading = False

    @rx.event
    def navigate(self, section: str):
        if section not in ["Notes", "Pinned", "Archive", "Trash"]:
            return
        self.section = section
        self.page = 0
        self.mobile_open = False
        self.pending_delete = 0
        if section == "Archive":
            return rx.redirect("/archive")
        if self.archive_route:
            self.archive_route = False
            return rx.redirect("/")
        return NotesState.refresh

    @rx.event
    def change_search(self, value: str):
        self.search = value[:500]
        self.page = 0
        return NotesState.refresh

    @rx.event
    def filter_label(self, value: int):
        self.label_filter = value
        self.page = 0
        return NotesState.refresh

    @rx.event
    def filter_color(self, value: str):
        self.color_filter = value
        self.page = 0
        return NotesState.refresh

    @rx.event
    def clear_filters(self):
        self.search = ""
        self.label_filter = 0
        self.color_filter = "all"
        self.page = 0
        return NotesState.refresh

    @rx.event
    def change_page(self, direction: int):
        self.page = max(0, self.page + direction)
        return NotesState.refresh

    @rx.event
    def toggle_grid(self):
        self.grid = not self.grid

    @rx.event
    def toggle_mobile(self):
        self.mobile_open = not self.mobile_open

    @rx.event
    def open_composer(self):
        self.composer_open = True

    @rx.event
    def close_composer(self):
        self.composer_open = False
        self.error = ""

    @rx.event
    def toggle_checklist(self):
        self.checklist_mode = not self.checklist_mode

    @rx.event
    def pick_color(self, value: str):
        if value in self.colors:
            self.draft_color = value

    @rx.event
    def pick_label(self, value: int):
        self.draft_label = value

    @rx.event
    def ask_delete(self, note_id: int):
        self.pending_delete = note_id

    @rx.event
    def cancel_delete(self):
        self.pending_delete = 0

    @rx.event
    async def create_note(self, form_data: dict[str, Any]):
        title = str(form_data.get("title", "")).strip()
        body = str(form_data.get("body", "")).strip()
        if not title and not body:
            self.error = "Add a title or a thought before saving."
            return
        if len(title) > 500 or len(body) > 20000:
            self.error = "Keep titles under 500 characters and notes under 20,000 characters."
            return
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if self.checklist_mode and (not lines or len(lines) > 100):
            self.error = "Add 1–100 checklist items, one per line."
            return
        self.saving = True
        self.error = ""
        yield
        try:
            async with rx.asession() as session:
                note_id = (
                    await session.execute(
                        text(
                            "INSERT INTO notes (title, plain_text_content, content_format, note_type, color) VALUES (:title, :body, 'plain', :kind, :color) RETURNING id"
                        ),
                        {
                            "title": title,
                            "body": body,
                            "kind": "checklist"
                            if self.checklist_mode
                            else "text",
                            "color": self.draft_color,
                        },
                    )
                ).scalar_one()
                if self.checklist_mode:
                    await session.execute(
                        text(
                            "INSERT INTO checklist_items (note_id, content, sort_order) VALUES (:id, :content, :position)"
                        ),
                        [
                            {"id": note_id, "content": line, "position": i}
                            for i, line in enumerate(lines)
                        ],
                    )
                if self.draft_label:
                    await session.execute(
                        text(
                            "INSERT INTO note_labels (note_id, label_id) SELECT :note, id FROM labels WHERE id=:label"
                        ),
                        {"note": note_id, "label": self.draft_label},
                    )
                await session.commit()
            self.composer_open = False
            self.form_version += 1
            self.checklist_mode = False
            self.draft_label = 0
            self.section = "Notes"
            self.search = ""
            self.label_filter = 0
            self.color_filter = "all"
            self.page = 0
            yield rx.toast("Thought saved.")
            yield NotesState.refresh
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.error = "Couldn't save this note. Your draft is still here; please try again."
        finally:
            self.saving = False

    @rx.event
    async def act(self, note_id: int, action: str):
        statements = {
            "pin": "UPDATE notes SET is_pinned=NOT is_pinned, updated_at=CURRENT_TIMESTAMP WHERE id=:id AND NOT is_trashed AND NOT is_archived",
            "archive": "UPDATE notes SET is_archived=TRUE, archived_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP WHERE id=:id AND NOT is_trashed",
            "trash": "UPDATE notes SET is_trashed=TRUE, trashed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP WHERE id=:id AND NOT is_trashed",
            "restore": "UPDATE notes SET is_trashed=FALSE, is_archived=FALSE, archived_at=NULL, trashed_at=NULL, updated_at=CURRENT_TIMESTAMP WHERE id=:id AND (is_trashed OR is_archived)",
            "delete": "DELETE FROM notes WHERE id=:id AND is_trashed=TRUE",
        }
        if action not in statements or (
            action == "delete" and self.pending_delete != note_id
        ):
            return
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text(statements[action]), {"id": note_id}
                )
                await session.commit()
            self.pending_delete = 0
            if not result.rowcount:
                yield rx.toast(
                    "This note has already changed. Refreshing your workspace."
                )
            else:
                yield rx.toast(
                    {
                        "pin": "Pin updated.",
                        "archive": "Moved to Archive.",
                        "trash": "Moved to Trash. You can restore it anytime.",
                        "restore": "Restored to Notes.",
                        "delete": "Note permanently deleted.",
                    }[action]
                )
            yield NotesState.refresh
        except Exception as e:
            logging.exception(f"Error: {e}")
            yield rx.toast("Couldn't update this note. Please try again.")
