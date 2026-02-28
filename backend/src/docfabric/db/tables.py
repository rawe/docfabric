import sqlalchemy as sa

metadata = sa.MetaData()

documents = sa.Table(
    "documents",
    metadata,
    sa.Column("id", sa.Text, primary_key=True),
    sa.Column("filename", sa.Text, nullable=False),
    sa.Column("content_type", sa.Text, nullable=False),
    sa.Column("size_bytes", sa.Integer, nullable=False),
    sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)
