import reflex as rx

import logging
from typing import Any, TypedDict
from sqlalchemy import text, bindparam
from app.states.notes_state import LabelData


class EditorItem(TypedDict):
    id: int
    content: str
    done: bool


class EditorState(rx.State):
    current_id: int = 0
    title: str = ""
    body: str = ""
    kind: str = "text"
    color: str = "paper"
    colors: list[str] = ["paper", "butter", "sage", "peach", "rose", "sky"]
    labels: list[LabelData] = []
    selected_labels: list[int] = []
    items: list[EditorItem] = []
    pinned: bool = False
    archived: bool = False
    trashed: bool = False
    created: str = ""
    updated: str = ""
    version: str = ""
    loading: bool = True
    found: bool = False
    dirty: bool = False
    saving: bool = False
    error: str = ""
    load_error: str = ""
    next_item: int = -1
    leave_open: bool = False

    @rx.var
    def status(self) -> str:
        if self.saving:
            return "Saving…"
        if self.error:
            return "Couldn't save"
        return "Unsaved changes" if self.dirty else "All changes saved"

    @rx.event
    async def load(self):
        self.loading = True
        self.found = False
        self.load_error = ""
        self.error = ""
        self.dirty = False
        self.leave_open = False
        self.current_id = 0
        raw = str(self.router.page.params.get("note_id", ""))
        if not raw.isdecimal() or len(raw) > 18 or int(raw) < 1:
            self.loading = False
            return
        try:
            async with rx.asession() as session:
                row = (
                    (
                        await session.execute(
                            text(
                                "SELECT id, title, plain_text_content, rich_text_content, content_format, note_type, color, is_pinned, is_archived, is_trashed, created_at, updated_at FROM notes WHERE id=:id"
                            ),
                            {"id": int(raw)},
                        )
                    )
                    .mappings()
                    .first()
                )
                if not row:
                    return
                item_rows = (
                    (
                        await session.execute(
                            text(
                                "SELECT id, content, is_completed FROM checklist_items WHERE note_id=:id ORDER BY sort_order, id"
                            ),
                            {"id": int(raw)},
                        )
                    )
                    .mappings()
                    .all()
                )
                labels = (
                    (
                        await session.execute(
                            text(
                                "SELECT id, name FROM labels ORDER BY sort_order, name"
                            )
                        )
                    )
                    .mappings()
                    .all()
                )
                links = (
                    (
                        await session.execute(
                            text(
                                "SELECT label_id FROM note_labels WHERE note_id=:id"
                            ),
                            {"id": int(raw)},
                        )
                    )
                    .scalars()
                    .all()
                )
            self.current_id = int(row["id"])
            self.title = str(row["title"] or "")
            self.body = str(
                (
                    row["rich_text_content"]
                    if row["content_format"] == "markdown"
                    else row["plain_text_content"]
                )
                or ""
            )
            self.kind = str(row["note_type"])
            self.color = str(row["color"])
            self.pinned = bool(row["is_pinned"])
            self.archived = bool(row["is_archived"])
            self.trashed = bool(row["is_trashed"])
            self.created = row["created_at"].strftime("%b %d, %Y · %H:%M %Z")
            self.updated = row["updated_at"].strftime("%b %d, %Y · %H:%M %Z")
            self.version = row["updated_at"].isoformat()
            self.items = [
                {
                    "id": int(i["id"]),
                    "content": str(i["content"]),
                    "done": bool(i["is_completed"]),
                }
                for i in item_rows
            ]
            self.labels = [
                {"id": int(i["id"]), "name": str(i["name"])} for i in labels
            ]
            self.selected_labels = [int(i) for i in links]
            self.next_item = -1
            self.found = True
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.load_error = "This page couldn't be loaded. Please try again."
        finally:
            self.loading = False

    @rx.event
    def change_title(self, value: str):
        self.title = value
        self.dirty = True

    @rx.event
    def change_body(self, value: str):
        self.body = value
        self.dirty = True

    @rx.event
    def switch_mode(self):
        self.kind = "checklist" if self.kind == "text" else "text"
        self.dirty = True

    @rx.event
    def pick_color(self, color: str):
        if color in self.colors:
            self.color = color
            self.dirty = True

    @rx.event
    def toggle_label(self, label: int):
        if label in self.selected_labels:
            self.selected_labels.remove(label)
        elif any(i["id"] == label for i in self.labels):
            self.selected_labels.append(label)
        self.dirty = True

    @rx.event
    def add_item(self):
        if len(self.items) >= 100:
            self.error = "Keep your checklist to 100 items."
            return
        self.items.append({"id": self.next_item, "content": "", "done": False})
        self.next_item -= 1
        self.dirty = True

    @rx.event
    def edit_item(self, item_id: int, value: str):
        for item in self.items:
            if item["id"] == item_id:
                item["content"] = value
                self.dirty = True

    @rx.event
    def item_action(self, item_id: int, action: str):
        index = next(
            (i for i, item in enumerate(self.items) if item["id"] == item_id),
            -1,
        )
        if index < 0:
            return
        if action == "toggle":
            self.items[index]["done"] = not self.items[index]["done"]
        elif action == "remove":
            self.items.pop(index)
        elif action in ("up", "down"):
            other = index + (-1 if action == "up" else 1)
            if 0 <= other < len(self.items):
                self.items[index], self.items[other] = (
                    self.items[other],
                    self.items[index],
                )
        self.dirty = True

    @rx.event
    def request_leave(self):
        if self.dirty:
            self.leave_open = True
        else:
            return rx.redirect("/")

    @rx.event
    def cancel_leave(self):
        self.leave_open = False

    @rx.event
    async def save(self, payload: dict[str, Any]):
        if self.saving or not self.found:
            return
        self.title = str(payload.get("title", self.title))
        self.body = str(payload.get("body", self.body))
        values = payload.get("items", {})
        for item in self.items:
            item["content"] = str(values.get(str(item["id"]), item["content"]))
        action = str(payload.get("action", "save"))
        self.dirty = True
        self.error = ""
        if (
            len(self.title) > 500
            or len(self.body) > 20000
            or any(len(i["content"]) > 2000 for i in self.items)
        ):
            self.error = "Use up to 500 title characters, 20,000 body characters, and 2,000 characters per item."
            return
        if (
            not self.title.strip()
            and not self.body.strip()
            and not any(i["content"].strip() for i in self.items)
        ):
            self.error = (
                "Give this thought a title, some text, or a checklist item."
            )
            return
        if any(not i["content"].strip() for i in self.items):
            self.error = (
                "Write something in each checklist item, or remove empty items."
            )
            return
        self.saving = True
        yield
        try:
            pinned = not self.pinned if action == "pin" else self.pinned
            archived = (
                not self.archived if action == "archive" else self.archived
            )
            trashed = not self.trashed if action == "trash" else self.trashed
            async with rx.asession() as session:
                changed = (
                    await session.execute(
                        text("""UPDATE notes SET title=:title, rich_text_content=:body, plain_text_content=:body,
                    content_format='markdown', note_type=:kind, color=:color, is_pinned=:pinned,
                    is_archived=:archived, is_trashed=:trashed,
                    archived_at=CASE WHEN :archived THEN COALESCE(archived_at, CURRENT_TIMESTAMP) ELSE NULL END,
                    trashed_at=CASE WHEN :trashed THEN COALESCE(trashed_at, CURRENT_TIMESTAMP) ELSE NULL END,
                    updated_at=CURRENT_TIMESTAMP WHERE id=:id AND updated_at=CAST(:version AS TIMESTAMP WITH TIME ZONE)
                    RETURNING updated_at"""),
                        {
                            "id": self.current_id,
                            "version": self.version,
                            "title": self.title.strip(),
                            "body": self.body,
                            "kind": self.kind,
                            "color": self.color,
                            "pinned": pinned,
                            "archived": archived,
                            "trashed": trashed,
                        },
                    )
                ).scalar_one_or_none()
                if changed is None:
                    self.error = "This note changed elsewhere or was deleted. Your draft is still here. Copy it before reloading to see the latest version."
                    return
                existing = [i["id"] for i in self.items if i["id"] > 0]
                await session.execute(
                    text(
                        "DELETE FROM checklist_items WHERE note_id=:note AND id NOT IN :ids"
                    ).bindparams(bindparam("ids", expanding=True)),
                    {"note": self.current_id, "ids": existing},
                )
                updates = [
                    {
                        "id": item["id"],
                        "note": self.current_id,
                        "content": item["content"],
                        "done": item["done"],
                        "position": position,
                    }
                    for position, item in enumerate(self.items)
                    if item["id"] > 0
                ]
                inserts = [
                    {
                        "note": self.current_id,
                        "content": item["content"],
                        "done": item["done"],
                        "position": position,
                    }
                    for position, item in enumerate(self.items)
                    if item["id"] < 0
                ]
                if updates:
                    await session.execute(
                        text(
                            "UPDATE checklist_items SET content=:content, is_completed=:done, sort_order=:position, updated_at=CURRENT_TIMESTAMP, completed_at=CASE WHEN :done THEN COALESCE(completed_at, CURRENT_TIMESTAMP) ELSE NULL END WHERE id=:id AND note_id=:note"
                        ),
                        updates,
                    )
                if inserts:
                    await session.execute(
                        text(
                            "INSERT INTO checklist_items (note_id, content, is_completed, sort_order, completed_at) VALUES (:note, :content, :done, :position, CASE WHEN :done THEN CURRENT_TIMESTAMP ELSE NULL END)"
                        ),
                        inserts,
                    )
                await session.execute(
                    text("DELETE FROM note_labels WHERE note_id=:id"),
                    {"id": self.current_id},
                )
                if self.selected_labels:
                    await session.execute(
                        text(
                            "INSERT INTO note_labels (note_id, label_id, sort_order) VALUES (:note, :label, :position)"
                        ),
                        [
                            {
                                "note": self.current_id,
                                "label": label,
                                "position": position,
                            }
                            for position, label in enumerate(
                                self.selected_labels
                            )
                        ],
                    )
                rows = (
                    (
                        await session.execute(
                            text(
                                "SELECT id, content, is_completed FROM checklist_items WHERE note_id=:id ORDER BY sort_order, id"
                            ),
                            {"id": self.current_id},
                        )
                    )
                    .mappings()
                    .all()
                )
                await session.commit()
            self.items = [
                {
                    "id": int(i["id"]),
                    "content": str(i["content"]),
                    "done": bool(i["is_completed"]),
                }
                for i in rows
            ]
            self.version = changed.isoformat()
            self.updated = changed.strftime("%b %d, %Y · %H:%M %Z")
            self.pinned, self.archived, self.trashed = pinned, archived, trashed
            self.dirty = False
            self.leave_open = False
            if action == "back":
                yield rx.redirect("/")
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.error = (
                "Couldn't save. Your draft is still here; please try again."
            )
        finally:
            self.saving = False
