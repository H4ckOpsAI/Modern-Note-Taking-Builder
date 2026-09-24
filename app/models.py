import reflex as rx

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (
        Index(
            "ix_notes_workspace",
            "is_trashed",
            "is_archived",
            "is_pinned",
            "sort_order",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(500), default="", server_default=""
    )
    rich_text_content: Mapped[str] = mapped_column(
        Text, default="", server_default=""
    )
    content_format: Mapped[str] = mapped_column(
        String(32), default="html", server_default="html"
    )
    plain_text_content: Mapped[str] = mapped_column(
        Text, default="", server_default=""
    )
    note_type: Mapped[str] = mapped_column(
        String(32), default="text", server_default="text"
    )
    color: Mapped[str] = mapped_column(
        String(32), default="paper", server_default="paper"
    )
    is_pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    is_trashed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    trashed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    checklist_items: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChecklistItem.sort_order",
    )
    label_links: Mapped[list["NoteLabel"]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    __table_args__ = (
        Index("ix_checklist_note_order", "note_id", "sort_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    note_id: Mapped[int | None] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"), nullable=True, default=None
    )
    content: Mapped[str] = mapped_column(Text, default="", server_default="")
    is_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    note: Mapped["Note | None"] = relationship(back_populates="checklist_items")


class Label(Base):
    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(120), default="", server_default="", index=True
    )
    color: Mapped[str] = mapped_column(
        String(32), default="paper", server_default="paper"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    note_links: Mapped[list["NoteLabel"]] = relationship(
        back_populates="label",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class NoteLabel(Base):
    __tablename__ = "note_labels"

    # The composite key prevents duplicate assignments; foreign keys are generated references.
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True
    )
    label_id: Mapped[int] = mapped_column(
        ForeignKey("labels.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    note: Mapped["Note"] = relationship(back_populates="label_links")
    label: Mapped["Label"] = relationship(back_populates="note_links")
