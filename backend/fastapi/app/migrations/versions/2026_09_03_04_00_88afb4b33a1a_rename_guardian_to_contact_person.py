"""rename_guardian_to_contact_person

Revision ID: 88afb4b33a1a
Revises: 691329bb2f8d
Create Date: 2026-09-03 04:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.modules.user.validation import ContactRelationEnum

revision: str = "88afb4b33a1a"
down_revision: str | Sequence[str] | None = "6a74a22d52e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_OLD_ENUM_NAME = "guardiantypeenum"
_NEW_ENUM_NAME = "contactrelationenum"
_OLD_TABLE = "guardians"
_NEW_TABLE = "contact_persons"
_COLUMN = "relation_to_user"


def upgrade() -> None:
  """Rename guardians → contact_persons and guardiantypeenum → contactrelationenum."""
  op.execute(f"ALTER INDEX ix_guardians_id RENAME TO ix_{_NEW_TABLE}_id")
  op.rename_table(_OLD_TABLE, _NEW_TABLE)

  new_enum = sa.Enum(ContactRelationEnum, name=_NEW_ENUM_NAME)
  new_enum.create(op.get_bind(), checkfirst=True)

  op.execute(
    f"ALTER TABLE {_NEW_TABLE} "
    f"ALTER COLUMN {_COLUMN} "
    f"TYPE {_NEW_ENUM_NAME} "
    f"USING {_COLUMN}::text::{_NEW_ENUM_NAME}"
  )

  op.execute(f"DROP TYPE IF EXISTS {_OLD_ENUM_NAME}")


def downgrade() -> None:
  """Revert the rename."""
  old_enum = sa.Enum(ContactRelationEnum, name=_OLD_ENUM_NAME)
  old_enum.create(op.get_bind(), checkfirst=True)

  op.execute(
    f"ALTER TABLE {_NEW_TABLE} "
    f"ALTER COLUMN {_COLUMN} "
    f"TYPE {_OLD_ENUM_NAME} "
    f"USING {_COLUMN}::text::{_OLD_ENUM_NAME}"
  )

  op.execute(f"DROP TYPE IF EXISTS {_NEW_ENUM_NAME}")

  op.rename_table(_NEW_TABLE, _OLD_TABLE)
  op.execute(f"ALTER INDEX ix_{_NEW_TABLE}_id RENAME TO ix_guardians_id")
