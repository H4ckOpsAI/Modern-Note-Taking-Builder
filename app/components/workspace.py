import reflex as rx

from app.states.notes_state import NotesState, NoteData, ItemData


def swatch(color: str) -> rx.Component:
    return rx.el.span(
        class_name=rx.match(
            color,
            (
                "butter",
                "block h-5 w-5 rounded-full border border-black/10 bg-[#f7e6a0]",
            ),
            (
                "sage",
                "block h-5 w-5 rounded-full border border-black/10 bg-[#dce5d3]",
            ),
            (
                "peach",
                "block h-5 w-5 rounded-full border border-black/10 bg-[#f3d4c2]",
            ),
            (
                "rose",
                "block h-5 w-5 rounded-full border border-black/10 bg-[#ecd5dc]",
            ),
            (
                "sky",
                "block h-5 w-5 rounded-full border border-black/10 bg-[#d5e5e9]",
            ),
            "block h-5 w-5 rounded-full border border-black/20 bg-[#fffdf8]",
        )
    )


def topbar() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.button(
                rx.icon("menu", class_name="h-5 w-5"),
                on_click=NotesState.toggle_mobile,
                aria_label="Toggle navigation",
                aria_expanded=NotesState.mobile_open,
                class_name="p-2 hover:bg-black/5 md:hidden",
            ),
            rx.icon("notebook-pen", class_name="h-6 w-6 shrink-0"),
            rx.el.span(
                "Paper & thought",
                class_name="text-lg font-semibold tracking-tight",
            ),
            class_name="flex shrink-0 items-center gap-3",
        ),
        rx.el.div(
            rx.icon(
                "search", class_name="h-4 w-4 shrink-0 text-[var(--muted)]"
            ),
            rx.el.input(
                placeholder="Find a thought…",
                aria_label="Search notes, checklist items, and labels in the current view",
                type="search",
                default_value=NotesState.search,
                on_change=NotesState.change_search.debounce(400),
                class_name="min-w-0 flex-1 bg-transparent py-2.5 text-sm text-[var(--ink)] outline-hidden placeholder:text-[var(--muted)]",
            ),
            class_name="order-3 flex w-full items-center gap-3 rounded-2xl border border-[var(--line)] bg-[var(--surface)] px-4 focus-within:border-[var(--ink)] sm:order-none sm:ml-auto sm:max-w-md",
        ),
        rx.el.button(
            rx.cond(
                NotesState.grid,
                rx.icon("list", class_name="h-5 w-5"),
                rx.icon("layout-grid", class_name="h-5 w-5"),
            ),
            rx.el.span(
                rx.cond(NotesState.grid, "List view", "Grid view"),
                class_name="hidden lg:inline",
            ),
            aria_label=rx.cond(
                NotesState.grid, "Switch to list view", "Switch to grid view"
            ),
            on_click=NotesState.toggle_grid,
            class_name="ml-auto flex items-center gap-2 border border-[var(--line)] bg-[var(--surface)] p-3 text-sm hover:bg-black/5 sm:ml-0",
        ),
        class_name="z-20 flex shrink-0 flex-wrap items-center gap-4 border-b border-[var(--line)] bg-[var(--paper)] px-5 py-4 sm:px-8 lg:gap-8",
    )


def nav_button(label: str, icon: str) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-[18px] w-[18px]"),
        label,
        rx.cond(
            NotesState.section == label,
            rx.el.span(
                class_name="ml-auto h-1.5 w-1.5 rounded-full bg-[var(--ink)]"
            ),
        ),
        on_click=NotesState.navigate(label),
        aria_pressed=NotesState.section == label,
        class_name=rx.cond(
            NotesState.section == label,
            "flex w-full items-center gap-3 bg-[#eae6d8] px-4 py-3 text-left text-sm font-semibold text-[var(--ink)]",
            "flex w-full items-center gap-3 bg-transparent px-4 py-3 text-left text-sm text-[var(--muted)] hover:bg-black/5 hover:text-[var(--ink)]",
        ),
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.nav(
            nav_button("Notes", "notebook"),
            nav_button("Pinned", "pin"),
            nav_button("Archive", "archive"),
            nav_button("Trash", "trash-2"),
            rx.el.div(
                rx.el.h2(
                    "LABELS",
                    class_name="mb-3 px-4 text-[10px] font-semibold tracking-[0.18em] text-[var(--muted)]",
                ),
                rx.el.button(
                    "All labels",
                    on_click=NotesState.filter_label(0),
                    aria_pressed=NotesState.label_filter == 0,
                    class_name=rx.cond(
                        NotesState.label_filter == 0,
                        "w-full bg-black/5 px-4 py-2 text-left text-sm font-semibold",
                        "w-full px-4 py-2 text-left text-sm text-[var(--muted)] hover:bg-black/5",
                    ),
                ),
                rx.foreach(
                    NotesState.labels,
                    lambda label: rx.el.button(
                        rx.icon("tag", class_name="h-3.5 w-3.5 shrink-0"),
                        rx.el.span(label["name"], class_name="truncate"),
                        key=label["id"],
                        on_click=NotesState.filter_label(label["id"]),
                        aria_pressed=NotesState.label_filter == label["id"],
                        class_name=rx.cond(
                            NotesState.label_filter == label["id"],
                            "flex w-full items-center gap-3 bg-black/5 px-4 py-2.5 text-left text-sm font-semibold",
                            "flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm text-[var(--muted)] hover:bg-black/5",
                        ),
                    ),
                ),
                class_name="mt-9",
            ),
            rx.el.div(
                rx.el.h2(
                    "A SPLASH OF COLOR",
                    class_name="mb-3 text-[10px] font-semibold tracking-[0.15em] text-[var(--muted)]",
                ),
                rx.el.div(
                    rx.foreach(
                        NotesState.colors,
                        lambda color: rx.el.button(
                            swatch(color),
                            title=color,
                            aria_label=f"Filter by {color}",
                            aria_pressed=NotesState.color_filter == color,
                            on_click=NotesState.filter_color(color),
                            class_name=rx.cond(
                                NotesState.color_filter == color,
                                "rounded-full! p-1 ring-1 ring-[var(--ink)] ring-offset-2 ring-offset-[var(--paper)]",
                                "rounded-full! p-1 hover:ring-1 hover:ring-black/30",
                            ),
                        ),
                    ),
                    class_name="flex flex-wrap gap-2.5",
                ),
                rx.el.button(
                    "All colors",
                    on_click=NotesState.filter_color("all"),
                    aria_pressed=NotesState.color_filter == "all",
                    class_name="mt-3 text-xs text-[var(--muted)] underline decoration-black/20 underline-offset-4 hover:text-[var(--ink)]",
                ),
                class_name="mt-9 px-4",
            ),
            aria_label="Workspace navigation and filters",
            class_name="flex min-h-0 flex-1 flex-col gap-1 overflow-y-auto px-3 py-7",
        ),
        rx.el.div(
            rx.icon("sprout", class_name="mb-3 h-6 w-6 text-[var(--muted)]"),
            rx.el.p("Less noise.", class_name="text-xs text-[var(--muted)]"),
            rx.el.p(
                "More possibility.",
                class_name="mt-1 text-xs text-[var(--muted)]",
            ),
            class_name="hidden shrink-0 px-7 pb-8 md:block",
        ),
        class_name=rx.cond(
            NotesState.mobile_open,
            "absolute inset-y-0 left-0 z-30 flex w-56 flex-col border-r border-[var(--line)] bg-[var(--paper)] md:static md:shrink-0",
            "hidden w-56 shrink-0 flex-col border-r border-[var(--line)] bg-[var(--paper)] md:flex",
        ),
    )


def composer() -> rx.Component:
    return rx.el.section(
        rx.el.button(
            rx.icon("plus", class_name="h-5 w-5"),
            rx.el.span("What's on your mind?", class_name="flex-1 text-left"),
            rx.icon("square-check", class_name="h-5 w-5 text-[var(--muted)]"),
            on_click=NotesState.open_composer,
            aria_expanded=NotesState.composer_open,
            class_name=rx.cond(
                NotesState.composer_open,
                "hidden",
                "flex w-full items-center gap-4 bg-[var(--surface)] px-6 py-5 text-sm text-[var(--muted)] hover:bg-white",
            ),
        ),
        rx.el.form(
            rx.el.div(
                rx.el.input(
                    name="title",
                    placeholder="Give your thought a title",
                    aria_label="Note title",
                    max_length=500,
                    class_name="w-full bg-transparent text-lg font-medium text-[var(--ink)] outline-hidden placeholder:text-[var(--muted)]",
                ),
                rx.el.textarea(
                    name="body",
                    placeholder=rx.cond(
                        NotesState.checklist_mode,
                        "One item per line…",
                        "A thought, a plan, a little possibility…",
                    ),
                    aria_label=rx.cond(
                        NotesState.checklist_mode,
                        "Checklist items, one per line",
                        "Note body",
                    ),
                    max_length=20000,
                    rows=4,
                    class_name="mt-4 w-full resize-y bg-transparent text-sm leading-7 text-[var(--ink)] outline-hidden placeholder:text-[var(--muted)]",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("square-check", class_name="h-4 w-4"),
                        rx.cond(
                            NotesState.checklist_mode,
                            "Checklist · one item per line",
                            "Make a checklist",
                        ),
                        type="button",
                        on_click=NotesState.toggle_checklist,
                        aria_pressed=NotesState.checklist_mode,
                        class_name=rx.cond(
                            NotesState.checklist_mode,
                            "flex items-center gap-2 bg-[#eae6d8] px-3 py-2 text-xs text-[var(--ink)]",
                            "flex items-center gap-2 px-3 py-2 text-xs text-[var(--muted)] hover:bg-black/5",
                        ),
                    ),
                    rx.el.div(
                        rx.foreach(
                            NotesState.colors,
                            lambda color: rx.el.button(
                                swatch(color),
                                title=color,
                                type="button",
                                aria_label=f"Use {color} note color",
                                aria_pressed=NotesState.draft_color == color,
                                on_click=NotesState.pick_color(color),
                                class_name=rx.cond(
                                    NotesState.draft_color == color,
                                    "rounded-full! p-1 ring-1 ring-[var(--ink)]",
                                    "rounded-full! p-1 hover:bg-black/5",
                                ),
                            ),
                        ),
                        role="group",
                        aria_label="Note color",
                        class_name="flex items-center gap-1",
                    ),
                    class_name="flex flex-wrap items-center justify-between gap-3",
                ),
                rx.el.div(
                    rx.icon(
                        "tag", class_name="h-3.5 w-3.5 text-[var(--muted)]"
                    ),
                    rx.el.button(
                        "No label",
                        type="button",
                        on_click=NotesState.pick_label(0),
                        aria_pressed=NotesState.draft_label == 0,
                        class_name=rx.cond(
                            NotesState.draft_label == 0,
                            "bg-[#eae6d8] px-2.5 py-1.5 text-xs",
                            "px-2.5 py-1.5 text-xs text-[var(--muted)] hover:bg-black/5",
                        ),
                    ),
                    rx.foreach(
                        NotesState.labels,
                        lambda label: rx.el.button(
                            label["name"],
                            type="button",
                            on_click=NotesState.pick_label(label["id"]),
                            aria_pressed=NotesState.draft_label == label["id"],
                            class_name=rx.cond(
                                NotesState.draft_label == label["id"],
                                "bg-[#eae6d8] px-2.5 py-1.5 text-xs",
                                "px-2.5 py-1.5 text-xs text-[var(--muted)] hover:bg-black/5",
                            ),
                        ),
                    ),
                    role="group",
                    aria_label="Note label",
                    class_name="mt-3 flex flex-wrap items-center gap-1",
                ),
                rx.cond(
                    NotesState.error != "",
                    rx.el.p(
                        NotesState.error,
                        role="alert",
                        class_name="mt-3 text-sm text-red-600",
                    ),
                ),
                class_name="p-5 sm:p-6",
            ),
            rx.el.div(
                rx.el.span(
                    "Make a little space for an idea.",
                    class_name="hidden text-xs text-[var(--muted)] sm:block",
                ),
                rx.el.div(
                    rx.el.button(
                        "Close",
                        type="button",
                        disabled=NotesState.saving,
                        on_click=NotesState.close_composer,
                        class_name="px-4 py-2.5 text-sm hover:bg-black/5 disabled:opacity-50",
                    ),
                    rx.el.button(
                        rx.cond(NotesState.saving, "Saving…", "Save thought"),
                        rx.icon("arrow-up-right", class_name="h-4 w-4"),
                        type="submit",
                        disabled=NotesState.saving,
                        class_name="flex items-center gap-2 bg-[var(--ink)] px-4 py-2.5 text-sm text-[var(--surface)] hover:bg-black disabled:opacity-50",
                    ),
                    class_name="ml-auto flex items-center gap-2",
                ),
                class_name="flex items-center justify-between gap-3 border-t border-[var(--line)] px-5 py-3",
            ),
            on_submit=NotesState.create_note,
            key=NotesState.form_version,
            class_name=rx.cond(
                NotesState.composer_open, "block bg-[var(--surface)]", "hidden"
            ),
        ),
        aria_label="Quick note composer",
        class_name="mb-10 w-full overflow-hidden rounded-[var(--radius-note)] border border-[var(--line)] bg-[var(--surface)]",
    )


def card_action(
    icon: str, label: str, event: rx.event.EventType
) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4"),
        aria_label=label,
        title=label,
        on_click=event,
        class_name="p-2 text-[var(--ink)] hover:bg-black/10 focus-visible:bg-black/10",
    )


def checklist_item(item: ItemData) -> rx.Component:
    return rx.el.li(
        rx.cond(
            item["done"],
            rx.icon(
                "square-check",
                class_name="mt-0.5 h-4 w-4 shrink-0 text-black/40",
            ),
            rx.icon(
                "square", class_name="mt-0.5 h-4 w-4 shrink-0 text-black/45"
            ),
        ),
        rx.el.span(
            item["content"],
            class_name=rx.cond(
                item["done"], "text-black/45 line-through", "text-[var(--ink)]"
            ),
        ),
        class_name="flex items-start gap-2.5 text-sm leading-6",
    )


def note_card(note: NoteData) -> rx.Component:
    return rx.el.article(
        rx.el.a(
            rx.el.div(
                rx.el.h3(
                    note["title"],
                    class_name="break-words text-lg font-semibold leading-snug tracking-[-0.025em] text-[var(--ink)]",
                ),
                rx.cond(
                    note["pinned"],
                    rx.icon(
                        "pin",
                        class_name="mt-1 h-3.5 w-3.5 shrink-0 text-black/50",
                    ),
                ),
                class_name="flex items-start justify-between gap-3",
            ),
            rx.cond(
                note["checklist"],
                rx.el.div(
                    rx.el.ul(
                        rx.foreach(note["items"], checklist_item),
                        class_name="mt-5 space-y-2",
                    ),
                    rx.el.p(
                        f"{note['completed']} of {note['total']} complete",
                        class_name="mt-4 text-[11px] font-medium text-black/50",
                    ),
                    rx.cond(
                        note["total"] > 5,
                        rx.el.p(
                            f"+ {note['total'] - 5} more items",
                            class_name="mt-1 text-xs text-black/50",
                        ),
                    ),
                ),
                rx.el.p(
                    note["body"],
                    class_name=rx.cond(
                        NotesState.grid,
                        "mt-4 line-clamp-9 whitespace-pre-line break-words text-sm leading-7 text-[var(--ink)]/85",
                        "mt-3 line-clamp-3 whitespace-pre-line break-words text-sm leading-7 text-[var(--ink)]/85",
                    ),
                ),
            ),
            rx.el.div(
                rx.foreach(
                    note["labels"],
                    lambda label: rx.el.span(
                        label,
                        class_name="w-fit rounded-full bg-black/5 px-2.5 py-1 text-[10px] font-medium text-black/60",
                    ),
                ),
                class_name="mt-5 flex flex-wrap gap-1.5",
            ),
            href=f"/note/{note['id']}",
            aria_label=f"Open {note['title']}",
            class_name="block min-w-0 flex-1 rounded-lg outline-offset-4 focus-visible:outline-2 focus-visible:outline-black/50",
        ),
        rx.el.div(
            rx.el.span(
                f"Edited {note['updated']}",
                class_name="text-[10px] text-black/50",
            ),
            rx.el.div(
                rx.cond(
                    note["trashed"],
                    rx.fragment(
                        card_action(
                            "undo-2",
                            "Restore to Notes",
                            NotesState.act(note["id"], "restore"),
                        ),
                        card_action(
                            "trash-2",
                            "Delete permanently",
                            NotesState.ask_delete(note["id"]),
                        ),
                    ),
                    rx.fragment(
                        rx.cond(
                            note["archived"],
                            card_action(
                                "archive-restore",
                                "Restore to Notes",
                                NotesState.act(note["id"], "restore"),
                            ),
                            rx.fragment(
                                card_action(
                                    "pin",
                                    rx.cond(
                                        note["pinned"], "Unpin note", "Pin note"
                                    ),
                                    NotesState.act(note["id"], "pin"),
                                ),
                                card_action(
                                    "archive",
                                    "Move to Archive",
                                    NotesState.act(note["id"], "archive"),
                                ),
                            ),
                        ),
                        card_action(
                            "trash-2",
                            "Move to Trash",
                            NotesState.act(note["id"], "trash"),
                        ),
                    ),
                ),
                class_name="flex items-center opacity-75 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100",
            ),
            class_name="mt-5 flex flex-wrap items-center justify-between gap-1 border-t border-black/10 pt-3",
        ),
        rx.cond(
            NotesState.pending_delete == note["id"],
            rx.el.div(
                rx.el.p(
                    "Delete this thought forever?",
                    class_name="text-sm font-semibold text-[var(--ink)]",
                ),
                rx.el.p(
                    "This cannot be undone.",
                    class_name="mt-1 text-xs text-[var(--muted)]",
                ),
                rx.el.div(
                    rx.el.button(
                        "Keep it",
                        on_click=NotesState.cancel_delete,
                        class_name="px-3 py-2 text-xs hover:bg-black/5",
                    ),
                    rx.el.button(
                        "Delete forever",
                        on_click=NotesState.act(note["id"], "delete"),
                        class_name="bg-red-600 px-3 py-2 text-xs text-white hover:bg-red-700",
                    ),
                    class_name="mt-3 flex items-center gap-2",
                ),
                role="alert",
                class_name="mt-4 rounded-xl border border-black/10 bg-[var(--surface)] p-4",
            ),
        ),
        key=note["id"],
        class_name=rx.match(
            note["color"],
            (
                "butter",
                "group mb-5 break-inside-avoid rounded-[var(--radius-note)] border border-black/5 bg-[#f7e6a0] p-5 sm:p-6",
            ),
            (
                "sage",
                "group mb-5 break-inside-avoid rounded-[var(--radius-note)] border border-black/5 bg-[#dce5d3] p-5 sm:p-6",
            ),
            (
                "peach",
                "group mb-5 break-inside-avoid rounded-[var(--radius-note)] border border-black/5 bg-[#f3d4c2] p-5 sm:p-6",
            ),
            (
                "rose",
                "group mb-5 break-inside-avoid rounded-[var(--radius-note)] border border-black/5 bg-[#ecd5dc] p-5 sm:p-6",
            ),
            (
                "sky",
                "group mb-5 break-inside-avoid rounded-[var(--radius-note)] border border-black/5 bg-[#d5e5e9] p-5 sm:p-6",
            ),
            "group mb-5 break-inside-avoid rounded-[var(--radius-note)] border border-black/10 bg-[var(--surface)] p-5 sm:p-6",
        ),
    )


def note_section(title: str, icon: str, notes: list[NoteData]) -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.icon(icon, class_name="h-3.5 w-3.5"),
            rx.el.h2(
                title,
                class_name="text-[11px] font-semibold uppercase tracking-[0.16em]",
            ),
            rx.el.span(
                notes.length(), class_name="text-[10px] text-[var(--muted)]"
            ),
            class_name="mb-5 flex items-center gap-2.5 text-[var(--muted)]",
        ),
        rx.el.div(
            rx.foreach(notes, note_card),
            class_name=rx.cond(
                NotesState.grid,
                "columns-1 gap-5 sm:columns-2 md:columns-1 lg:columns-2 xl:columns-3 2xl:columns-4",
                "flex w-full flex-col [&>article]:w-full",
            ),
        ),
        class_name="mb-7",
    )


def empty_state() -> rx.Component:
    return rx.el.div(
        rx.icon(
            "notebook-pen", class_name="mb-5 h-10 w-10 text-[var(--muted)]"
        ),
        rx.el.h2(
            rx.cond(
                NotesState.filtered,
                "No thoughts found",
                rx.match(
                    NotesState.section,
                    ("Trash", "Nothing thrown away"),
                    ("Archive", "A little room for later"),
                    ("Pinned", "Keep a thought close"),
                    "A fresh page, just for you",
                ),
            ),
            class_name="text-2xl font-medium tracking-tight",
        ),
        rx.el.p(
            rx.cond(
                NotesState.filtered,
                "Try another search, label, or color. Search stays within your selected view.",
                rx.match(
                    NotesState.section,
                    (
                        "Trash",
                        "Deleted notes live here until you restore or permanently delete them.",
                    ),
                    (
                        "Archive",
                        "Archive a note to set it aside without saying goodbye.",
                    ),
                    (
                        "Pinned",
                        "Pin a note from Notes to keep it at the top of your workspace.",
                    ),
                    "Start with a small thought. The rest will follow.",
                ),
            ),
            class_name="mt-3 max-w-md text-center text-sm leading-6 text-[var(--muted)]",
        ),
        rx.cond(
            NotesState.filtered,
            rx.el.button(
                "Clear filters",
                on_click=NotesState.clear_filters,
                class_name="mt-6 border border-[var(--line)] bg-[var(--surface)] px-4 py-2.5 text-sm hover:bg-black/5",
            ),
            rx.el.button(
                "Back to Notes",
                on_click=NotesState.navigate("Notes"),
                class_name="mt-6 border border-[var(--line)] bg-[var(--surface)] px-4 py-2.5 text-sm hover:bg-black/5",
            ),
        ),
        class_name="flex min-h-80 flex-col items-center justify-center rounded-3xl border border-dashed border-[var(--line)] px-6 py-12",
    )


def workspace(archived: bool = False) -> rx.Component:
    return rx.el.div(
        topbar(),
        rx.el.div(
            rx.cond(
                NotesState.mobile_open,
                rx.el.button(
                    aria_label="Close navigation",
                    on_click=NotesState.toggle_mobile,
                    class_name="absolute inset-0 z-20 rounded-none! bg-black/20 md:hidden",
                ),
            ),
            sidebar(),
            rx.el.main(
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            "YOUR LITTLE CORNER OF CLARITY",
                            class_name="text-[10px] font-semibold tracking-[0.19em] text-[var(--muted)]",
                        ),
                        rx.el.h1(
                            rx.match(
                                NotesState.section,
                                ("Notes", "Space for your thoughts."),
                                ("Pinned", "The thoughts you keep close."),
                                ("Archive", "Set aside. Not forgotten."),
                                "A second thought?",
                            ),
                            class_name="mt-3 text-3xl font-medium leading-tight tracking-[-0.045em] sm:text-[40px]",
                        ),
                        rx.el.p(
                            rx.match(
                                NotesState.section,
                                (
                                    "Notes",
                                    "Little ideas. Big plans. Everything in between.",
                                ),
                                (
                                    "Pinned",
                                    "Your important ideas, always within reach.",
                                ),
                                (
                                    "Archive",
                                    "A quieter shelf for the things you might return to.",
                                ),
                                "Restore a note, or make room for something new.",
                            ),
                            class_name="mt-3 text-sm leading-6 text-[var(--muted)]",
                        ),
                        class_name="mb-8",
                    ),
                    rx.cond(
                        archived,
                        rx.el.div(
                            rx.icon("archive", class_name="h-5 w-5 shrink-0"),
                            rx.el.p(
                                "Your quieter shelf. Open a thought to revisit it, or restore it to your everyday workspace.",
                                class_name="text-sm leading-6",
                            ),
                            class_name="mb-9 flex items-center gap-4 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-5 text-[var(--muted)]",
                        ),
                        composer(),
                    ),
                    rx.cond(
                        NotesState.filtered,
                        rx.el.div(
                            rx.icon("filter", class_name="h-3.5 w-3.5"),
                            rx.el.span("Filtered view", class_name="text-xs"),
                            rx.el.button(
                                "Clear filters",
                                on_click=NotesState.clear_filters,
                                class_name="ml-auto text-xs underline underline-offset-4",
                            ),
                            class_name="mb-6 flex items-center gap-2 text-[var(--muted)]",
                        ),
                    ),
                    rx.cond(
                        NotesState.loading,
                        rx.el.div(
                            rx.foreach(
                                [0, 1, 2],
                                lambda i: rx.el.div(
                                    key=i,
                                    class_name="h-56 animate-pulse rounded-[var(--radius-note)] bg-[#eae6d8]",
                                ),
                            ),
                            role="status",
                            aria_label="Loading notes",
                            class_name="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3",
                        ),
                        rx.cond(
                            NotesState.load_error != "",
                            rx.el.div(
                                rx.el.p(
                                    NotesState.load_error,
                                    role="alert",
                                    class_name="text-sm text-red-600",
                                ),
                                rx.el.button(
                                    "Try again",
                                    on_click=NotesState.load,
                                    class_name="mt-4 border border-[var(--line)] bg-[var(--surface)] px-4 py-2 text-sm",
                                ),
                                class_name="rounded-2xl border border-[var(--line)] p-8",
                            ),
                            rx.cond(
                                NotesState.notes.length() == 0,
                                empty_state(),
                                rx.el.div(
                                    rx.cond(
                                        NotesState.pinned_notes.length() > 0,
                                        note_section(
                                            "Pinned",
                                            "pin",
                                            NotesState.pinned_notes,
                                        ),
                                    ),
                                    rx.cond(
                                        NotesState.recent_notes.length() > 0,
                                        note_section(
                                            rx.match(
                                                NotesState.section,
                                                (
                                                    "Archive",
                                                    "Archived thoughts",
                                                ),
                                                ("Trash", "In the trash"),
                                                "Recent thoughts",
                                            ),
                                            "clock-3",
                                            NotesState.recent_notes,
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    rx.cond(
                        (NotesState.page > 0) | NotesState.has_more,
                        rx.el.div(
                            rx.el.button(
                                "Previous",
                                disabled=(NotesState.page == 0)
                                | NotesState.loading,
                                on_click=NotesState.change_page(-1),
                                class_name="border border-[var(--line)] bg-[var(--surface)] px-4 py-2 text-sm disabled:opacity-40",
                            ),
                            rx.el.span(
                                f"Page {NotesState.page + 1}",
                                class_name="text-xs text-[var(--muted)]",
                            ),
                            rx.el.button(
                                "Next",
                                disabled=(~NotesState.has_more)
                                | NotesState.loading,
                                on_click=NotesState.change_page(1),
                                class_name="border border-[var(--line)] bg-[var(--surface)] px-4 py-2 text-sm disabled:opacity-40",
                            ),
                            class_name="mt-4 flex items-center justify-center gap-5",
                        ),
                    ),
                    rx.el.footer(
                        "A little less in your head. A little more on paper.",
                        class_name="mt-10 pb-3 text-center text-[11px] text-[var(--muted)]",
                    ),
                    class_name="w-full px-5 py-8 sm:px-8 lg:px-10 lg:py-10 xl:px-12",
                ),
                id="main-content",
                class_name="min-w-0 flex-1 overflow-y-auto",
            ),
            class_name="relative flex min-h-0 flex-1",
        ),
        class_name="flex h-dvh w-full flex-col overflow-hidden bg-[var(--paper)] font-['Inter'] text-[var(--ink)] antialiased [--paper:#f7f5ef] [--surface:#fffdf8] [--ink:#292a24] [--muted:#77776c] [--line:#e3e0d5] [--radius-note:1.25rem] [--radius-control:0.875rem] selection:bg-[#f7e6a0] [&_button]:cursor-pointer [&_button]:rounded-[var(--radius-control)] [&_button]:transition-colors [&_button:focus-visible]:outline-2 [&_button:focus-visible]:outline-offset-4 [&_button:focus-visible]:outline-[var(--ink)] [&_button:disabled]:cursor-wait",
    )
