"""Add name column to users table

Revision ID: 6d62029bb66e
Revises: 001_initial_migration
Create Date: 2025-07-26 01:20:41.091056

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "6d62029bb66e"
down_revision = "001_initial_migration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add name column to users table
    op.add_column(
        "users",
        sa.Column(
            "name", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=""
        ),
    )

    # Remove the server default after adding the column
    op.alter_column("users", "name", server_default=None)

    # Drop the created_at and updated_at columns that aren't in the model
    op.drop_column("users", "created_at")
    op.drop_column("users", "updated_at")


def downgrade() -> None:
    # Add back the timestamp columns
    op.add_column(
        "users",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # Remove the name column
    op.drop_column("users", "name")
