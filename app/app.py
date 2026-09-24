import reflex as rx

from app.models import Base
from app.components.workspace import workspace
from app.states.notes_state import NotesState
from app.states.editor_state import EditorState
from app.components.editor import editor
from app.components.archive import archive

# Keep model metadata discoverable without opening a database connection.
model_metadata = Base.metadata


def index() -> rx.Component:
    return workspace()


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            cross_origin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(
    index,
    route="/",
    on_load=NotesState.load_workspace,
    title="Paper & thought",
    description="A quieter home for notes, lists, and ideas.",
)
app.add_page(
    editor,
    route="/note/[note_id]",
    on_load=EditorState.load,
    title="A thought on paper",
)
app.add_page(
    archive,
    route="/archive",
    on_load=NotesState.load_archive,
    title="Archive · Paper & thought",
)
