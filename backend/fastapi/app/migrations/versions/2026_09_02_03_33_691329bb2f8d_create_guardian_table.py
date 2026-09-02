"""create_guardian_table

Revision ID: 691329bb2f8d
Revises: 1684c5abd171
Create Date: 2026-09-02 03:33:35.310812

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.modules.user.validation import GuardianTypeEnum, PreferredContactEnum

# revision identifiers, used by Alembic.
revision: str = "691329bb2f8d"
down_revision: str | Sequence[str] | None = "1684c5abd171"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  """Upgrade schema."""
  sa_guardian_type_enum = sa.Enum(GuardianTypeEnum, name="guardiantypeenum")
  sa_preferred_contact_enum = sa.Enum(PreferredContactEnum, name="preferredcontactenum")

  op.create_table(
    "guardians",
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("first_name", sa.String(), nullable=False),
    sa.Column("last_name", sa.String(), nullable=False),
    sa.Column("email", sa.String(), nullable=True),
    sa.Column("phone_number", sa.String(), nullable=True),
    sa.Column("alternate_phone_number", sa.String(), nullable=True),
    sa.Column("address", sa.String(), nullable=True),
    sa.Column("occupation", sa.String(), nullable=True),
    sa.Column(
      "relation_to_user",
      type_=sa_guardian_type_enum,
      nullable=False,
    ),
    sa.Column(
      "is_primary_contact",
      sa.Boolean(),
      server_default=sa.text("false"),
      nullable=False,
    ),
    sa.Column(
      "is_emergency_contact",
      sa.Boolean(),
      server_default=sa.text("false"),
      nullable=False,
    ),
    sa.Column(
      "preferred_contact_method",
      type_=sa_preferred_contact_enum,
      nullable=False,
    ),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column(
      "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
    ),
    sa.Column(
      "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
    ),
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(
      ["user_id"],
      ["users.id"],
    ),
    sa.PrimaryKeyConstraint("user_id", "id"),
    sa.UniqueConstraint("email"),
  )
  op.create_index(op.f("ix_guardians_id"), "guardians", ["id"], unique=False)

  # Add alternate_phone_number column to users table
  op.add_column(
    "users", sa.Column("alternate_phone_number", sa.String(), nullable=True)
  )


def downgrade() -> None:
  """Downgrade schema."""
  # Drop alternate_phone_number column from users table
  op.drop_column("users", "alternate_phone_number")

  op.drop_index(op.f("ix_guardians_id"), table_name="guardians")
  op.drop_table("guardians")

  sa_preferred_contact_enum = sa.Enum(PreferredContactEnum, name="preferredcontactenum")
  sa_preferred_contact_enum.drop(op.get_bind(), checkfirst=True)

  sa_guardian_type_enum = sa.Enum(GuardianTypeEnum, name="guardiantypeenum")
  sa_guardian_type_enum.drop(op.get_bind(), checkfirst=True)
