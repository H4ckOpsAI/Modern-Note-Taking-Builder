import reflex as rx

from app.components.workspace import workspace


def archive() -> rx.Component:
    return workspace(archived=True)
