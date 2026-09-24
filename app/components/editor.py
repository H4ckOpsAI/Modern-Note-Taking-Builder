import reflex as rx

import json
from app.states.editor_state import EditorState, EditorItem
from app.components.workspace import swatch


def save_control(
    label: str, action: str = "save", icon: str = "check"
) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4"),
        label,
        on_click=rx.call_script(
            f"(() => ({{title: document.getElementById('note-title').value, body: document.getElementById('note-body').value, items: Object.fromEntries(Array.from(document.querySelectorAll('[data-item-id]')).map(e => [e.dataset.itemId, e.value])), action: {json.dumps(action)}}}))()",
            callback=EditorState.save,
        ),
        disabled=EditorState.saving,
        class_name="flex items-center justify-center gap-2 rounded-xl border border-black/15 bg-[#fffdf8] px-4 py-2.5 text-sm text-[#292a24] hover:bg-[#eae6d8] disabled:opacity-50",
    )


def format_control(
    label: str, icon: str, prefix: str, suffix: str = ""
) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4"),
        rx.el.span(label, class_name="sr-only"),
        title=label,
        on_click=rx.call_script(
            f"(() => {{ const e = document.getElementById('note-body'); const a=e.selectionStart, b=e.selectionEnd; const p={json.dumps(prefix)}, s={json.dumps(suffix)}; const selected=e.value.slice(a,b) || 'text'; const value=e.value.slice(0,a)+p+selected+s+e.value.slice(b); e.focus(); return value; }})()",
            callback=EditorState.change_body,
        ),
        class_name="rounded-lg p-3 text-[#292a24] hover:bg-black/5",
    )


def item_row(item: EditorItem, index: int) -> rx.Component:
    return rx.el.li(
        rx.el.button(
            rx.icon(
                rx.cond(item["done"], "square-check", "square"),
                class_name="h-5 w-5",
            ),
            on_click=EditorState.item_action(item["id"], "toggle"),
            aria_label="Toggle completion",
            aria_pressed=item["done"],
            class_name="rounded-lg p-2 hover:bg-black/5",
        ),
        rx.el.input(
            default_value=item["content"],
            custom_attrs={"data-item-id": item["id"]},
            on_change=lambda value: EditorState.edit_item(
                item["id"], value
            ).debounce(500),
            aria_label=f"Checklist item {index + 1}",
            placeholder="Something to do…",
            max_length=2000,
            class_name=rx.cond(
                item["done"],
                "min-w-0 flex-1 bg-transparent py-3 text-sm text-black/45 line-through",
                "min-w-0 flex-1 bg-transparent py-3 text-sm text-[#292a24]",
            ),
        ),
        rx.el.button(
            rx.icon("arrow-up", class_name="h-4 w-4"),
            aria_label="Move item up",
            disabled=index == 0,
            on_click=EditorState.item_action(item["id"], "up"),
            class_name="rounded-lg p-2 hover:bg-black/5 disabled:opacity-25",
        ),
        rx.el.button(
            rx.icon("arrow-down", class_name="h-4 w-4"),
            aria_label="Move item down",
            disabled=index == EditorState.items.length() - 1,
            on_click=EditorState.item_action(item["id"], "down"),
            class_name="rounded-lg p-2 hover:bg-black/5 disabled:opacity-25",
        ),
        rx.el.button(
            rx.icon("x", class_name="h-4 w-4"),
            aria_label="Remove item",
            on_click=EditorState.item_action(item["id"], "remove"),
            class_name="rounded-lg p-2 hover:bg-red-100",
        ),
        key=item["id"],
        class_name="flex items-center gap-1 border-b border-black/10",
    )


def details() -> rx.Component:
    return rx.el.aside(
        rx.el.h2(
            "The little details",
            class_name="text-lg font-medium tracking-tight",
        ),
        rx.el.p(
            "COLOR",
            class_name="mt-6 mb-3 text-[10px] font-semibold tracking-[0.16em] text-[#77776c]",
        ),
        rx.el.div(
            rx.foreach(
                EditorState.colors,
                lambda color: rx.el.button(
                    swatch(color),
                    on_click=EditorState.pick_color(color),
                    aria_label=f"Use {color}",
                    aria_pressed=EditorState.color == color,
                    class_name=rx.cond(
                        EditorState.color == color,
                        "rounded-full p-1 ring-1 ring-[#292a24]",
                        "rounded-full p-1 hover:bg-black/5",
                    ),
                ),
            ),
            class_name="flex flex-wrap gap-2",
        ),
        rx.el.p(
            "LABELS · CHOOSE A FEW",
            class_name="mt-7 mb-3 text-[10px] font-semibold tracking-[0.16em] text-[#77776c]",
        ),
        rx.el.div(
            rx.foreach(
                EditorState.labels,
                lambda label: rx.el.button(
                    rx.icon("tag", class_name="h-3 w-3"),
                    label["name"],
                    on_click=EditorState.toggle_label(label["id"]),
                    aria_pressed=EditorState.selected_labels.contains(
                        label["id"]
                    ),
                    class_name=rx.cond(
                        EditorState.selected_labels.contains(label["id"]),
                        "flex w-fit items-center gap-2 rounded-full border border-black/20 bg-[#eae6d8] px-3 py-2 text-xs",
                        "flex w-fit items-center gap-2 rounded-full border border-black/10 bg-transparent px-3 py-2 text-xs hover:bg-black/5",
                    ),
                ),
            ),
            class_name="flex flex-wrap gap-2",
        ),
        rx.cond(
            EditorState.labels.length() == 0,
            rx.el.p(
                "No labels in this workspace yet.",
                class_name="text-xs text-[#77776c]",
            ),
        ),
        rx.el.div(
            save_control(
                rx.cond(EditorState.pinned, "Unpin thought", "Pin thought"),
                "pin",
                "pin",
            ),
            save_control(
                rx.cond(
                    EditorState.archived, "Unarchive thought", "Archive thought"
                ),
                "archive",
                "archive",
            ),
            save_control(
                rx.cond(
                    EditorState.trashed, "Restore from trash", "Move to trash"
                ),
                "trash",
                "trash-2",
            ),
            rx.el.p(
                "These actions also save your edits. Trashed notes can be restored from the workspace.",
                class_name="text-xs leading-5 text-[#77776c]",
            ),
            class_name="mt-7 flex flex-col gap-2",
        ),
        rx.el.div(
            rx.el.p("Created"),
            rx.el.p(EditorState.created, class_name="mt-1 text-[#292a24]"),
            rx.el.p("Last saved", class_name="mt-4"),
            rx.el.p(EditorState.updated, class_name="mt-1 text-[#292a24]"),
            class_name="mt-7 border-t border-black/10 pt-5 text-xs leading-5 text-[#77776c]",
        ),
        class_name="w-full shrink-0 rounded-3xl border border-[#e3e0d5] bg-[#f7f5ef] p-6 lg:w-64 lg:self-start",
    )


def canvas() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                "A LITTLE SPACE TO THINK",
                class_name="text-[10px] font-semibold tracking-[0.18em] text-black/50",
            ),
            rx.el.input(
                id="note-title",
                default_value=EditorState.title,
                on_change=EditorState.change_title.debounce(500),
                aria_label="Note title",
                placeholder="Untitled thought",
                max_length=500,
                class_name="mt-6 w-full bg-transparent text-3xl font-medium leading-tight tracking-[-0.04em] text-[#292a24] outline-hidden focus-visible:ring-1 focus-visible:ring-black/20 sm:text-4xl",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon(
                        rx.cond(
                            EditorState.kind == "text", "square-check", "type"
                        ),
                        class_name="h-4 w-4",
                    ),
                    rx.cond(
                        EditorState.kind == "text",
                        "Switch to checklist",
                        "Switch to text",
                    ),
                    on_click=EditorState.switch_mode,
                    class_name="flex items-center gap-2 rounded-xl border border-black/15 px-3 py-2 text-xs hover:bg-black/5",
                ),
                rx.el.span(
                    "Text and checklist items are kept in both modes.",
                    class_name="text-xs text-black/50",
                ),
                class_name="mt-6 flex flex-wrap items-center gap-3",
            ),
            rx.el.div(
                rx.el.h2("Checklist", class_name="mt-8 text-lg font-medium"),
                rx.el.ul(
                    rx.foreach(EditorState.items, item_row), class_name="mt-2"
                ),
                rx.cond(
                    EditorState.items.length() == 0,
                    rx.el.p(
                        "One small step at a time. Add your first item.",
                        class_name="mt-4 text-sm text-black/50",
                    ),
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "Add item",
                    on_click=EditorState.add_item,
                    class_name="mt-4 flex items-center gap-2 rounded-xl px-3 py-2 text-sm hover:bg-black/5",
                ),
                class_name=rx.cond(
                    EditorState.kind == "checklist", "block", "hidden"
                ),
            ),
            rx.el.div(
                format_control("Heading", "heading", "\n## "),
                format_control("Bold", "bold", "**", "**"),
                format_control("Italic", "italic", "*", "*"),
                format_control("Bullet", "list", "\n- "),
                format_control("Quote", "quote", "\n> "),
                format_control(
                    "Link (edit the URL)", "link", "[", "](https://example.com)"
                ),
                role="toolbar",
                aria_label="Markdown formatting for selected text",
                class_name="mt-8 flex flex-wrap gap-1 border-y border-black/10 py-1",
            ),
            rx.el.p(
                "Select text to format it, or place your cursor to insert. Links use [text](https://…).",
                class_name="mt-3 text-[11px] leading-5 text-black/50",
            ),
            rx.el.textarea(
                id="note-body",
                on_change=EditorState.change_body,
                max_length=20000,
                aria_label="Markdown note body",
                placeholder="Let a thought find its way onto the page…",
                class_name="mt-5 min-h-80 w-full resize-y bg-transparent text-base leading-8 text-[#292a24] outline-hidden focus-visible:ring-1 focus-visible:ring-black/20",
                default_value=EditorState.body,
            ),
            rx.el.p(
                f"{EditorState.body.length()} / 20,000 characters",
                class_name="text-right text-[10px] text-black/45",
            ),
            class_name=rx.match(
                EditorState.color,
                ("butter", "rounded-t-3xl bg-[#f7e6a0] p-6 sm:p-10"),
                ("sage", "rounded-t-3xl bg-[#dce5d3] p-6 sm:p-10"),
                ("peach", "rounded-t-3xl bg-[#f3d4c2] p-6 sm:p-10"),
                ("rose", "rounded-t-3xl bg-[#ecd5dc] p-6 sm:p-10"),
                ("sky", "rounded-t-3xl bg-[#d5e5e9] p-6 sm:p-10"),
                "rounded-t-3xl bg-[#fffdf8] p-6 sm:p-10",
            ),
        ),
        rx.el.section(
            rx.el.div(
                rx.icon("book-open", class_name="h-4 w-4"),
                "ON THE PAGE · LIVE PREVIEW",
                class_name="mb-8 flex items-center gap-2 text-[10px] font-semibold tracking-[0.15em] text-[#77776c]",
            ),
            rx.el.h2(
                rx.cond(
                    EditorState.title != "",
                    EditorState.title,
                    "Untitled thought",
                ),
                class_name="mb-6 break-words text-3xl font-medium tracking-tight",
            ),
            rx.cond(
                EditorState.body != "",
                rx.markdown(
                    EditorState.body,
                    use_raw=False,
                    use_math=False,
                    use_katex=False,
                    class_name="break-words text-[#292a24] [&_p]:my-4 [&_p]:leading-8 [&_h1]:text-3xl [&_h2]:text-2xl [&_h3]:text-xl [&_ul]:list-disc [&_ul]:pl-6 [&_blockquote]:border-l-2 [&_blockquote]:border-[#d6c68a] [&_blockquote]:pl-5 [&_a]:underline",
                ),
                rx.el.p(
                    "Your words will take shape here.",
                    class_name="text-sm text-[#77776c]",
                ),
            ),
            class_name="min-h-64 rounded-b-3xl border-t border-[#e3e0d5] bg-[#fffdf8] p-6 sm:p-10",
        ),
        class_name="min-w-0 flex-1 rounded-3xl border border-black/10",
    )


def editor() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.button(
                rx.icon("arrow-left", class_name="h-4 w-4"),
                "Workspace",
                on_click=EditorState.request_leave,
                class_name="flex items-center gap-2 rounded-xl p-3 text-sm hover:bg-black/5",
            ),
            rx.el.a(
                rx.icon("notebook-pen", class_name="h-5 w-5"),
                "Paper & thought",
                href="/",
                class_name="hidden items-center gap-3 text-lg font-semibold sm:flex",
            ),
            rx.el.span(
                EditorState.status,
                role="status",
                aria_live="polite",
                class_name="ml-auto text-xs text-[#77776c]",
            ),
            rx.cond(EditorState.found, save_control("Save thought")),
            class_name="flex flex-wrap items-center gap-3 border-b border-[#e3e0d5] px-4 py-4 sm:px-8",
        ),
        rx.cond(
            EditorState.loading,
            rx.el.div(
                "Opening your thought…",
                role="status",
                class_name="m-8 min-h-80 animate-pulse rounded-3xl bg-[#eae6d8] p-10",
            ),
            rx.cond(
                EditorState.found,
                rx.el.div(
                    rx.cond(
                        EditorState.error != "",
                        rx.el.div(
                            EditorState.error,
                            role="alert",
                            class_name="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700",
                        ),
                    ),
                    rx.cond(
                        EditorState.archived | EditorState.trashed,
                        rx.el.p(
                            rx.cond(
                                EditorState.trashed,
                                "This thought is in Trash. You can still edit it or restore it below.",
                                "Set aside, not forgotten. This thought is archived.",
                            ),
                            class_name="mb-5 rounded-xl bg-[#eae6d8] p-4 text-sm",
                        ),
                    ),
                    rx.el.fieldset(
                        canvas(),
                        details(),
                        disabled=EditorState.saving,
                        class_name="flex min-w-0 flex-col items-stretch gap-6 border-0 p-0 lg:flex-row",
                    ),
                    class_name="mx-auto w-full max-w-[1440px] px-4 py-7 sm:px-8 lg:py-10",
                ),
                rx.el.div(
                    rx.icon(
                        "notebook", class_name="mb-5 h-10 w-10 text-[#77776c]"
                    ),
                    rx.el.h1(
                        rx.cond(
                            EditorState.load_error != "",
                            "A little trouble opening this page",
                            "This thought isn't here",
                        ),
                        class_name="text-2xl font-medium",
                    ),
                    rx.el.p(
                        rx.cond(
                            EditorState.load_error != "",
                            EditorState.load_error,
                            "It may have been deleted, or the link may be incomplete.",
                        ),
                        class_name="mt-3 text-sm text-[#77776c]",
                    ),
                    rx.el.button(
                        "Try again",
                        on_click=EditorState.load,
                        class_name="mt-6 rounded-xl border border-black/15 px-4 py-2",
                    ),
                    rx.el.a(
                        "Back to workspace",
                        href="/",
                        class_name="mt-4 text-sm underline",
                    ),
                    class_name="flex min-h-96 flex-col items-center justify-center p-8 text-center",
                ),
            ),
        ),
        rx.cond(
            EditorState.leave_open,
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Keep this thought?", class_name="text-xl font-medium"
                    ),
                    rx.el.p(
                        "You have unsaved changes. Save them before returning to the workspace.",
                        class_name="my-4 text-sm leading-6 text-[#77776c]",
                    ),
                    rx.el.div(
                        save_control("Save & return", "back"),
                        rx.el.button(
                            "Keep editing",
                            on_click=EditorState.cancel_leave,
                            class_name="rounded-xl border border-black/15 px-4 py-2 text-sm",
                        ),
                        rx.el.a(
                            "Discard & return",
                            href="/",
                            class_name="p-3 text-sm underline",
                        ),
                        class_name="flex flex-wrap gap-2",
                    ),
                    role="dialog",
                    aria_modal=True,
                    aria_label="Unsaved changes",
                    class_name="w-full max-w-lg rounded-3xl border border-[#e3e0d5] bg-[#fffdf8] p-7",
                ),
                class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/25 p-5",
            ),
        ),
        class_name="min-h-dvh bg-[#f7f5ef] font-['Inter'] text-[#292a24] antialiased selection:bg-[#f7e6a0] [&_button]:cursor-pointer [&_button:focus-visible]:outline-2 [&_button:focus-visible]:outline-offset-2 [&_a:focus-visible]:outline-2",
    )
