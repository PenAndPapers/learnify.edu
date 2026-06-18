from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core import BaseTable

from .validation import TokenTypeEnum


class TokenTable(BaseTable):
  __tablename__ = "tokens"

  user_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("users.id", ondelete="CASCADE")
  )
  token: Mapped[str] = mapped_column(String, unique=True, index=True)
  token_type: Mapped[TokenTypeEnum] = mapped_column(
    Enum(TokenTypeEnum), default=TokenTypeEnum.EMAIL_VERIFICATION
  )

  expires_at: Mapped[datetime] = mapped_column(DateTime)
  is_revoked: Mapped[bool] = mapped_column(Boolean, server_default="false")
  family_id: Mapped[str | None] = mapped_column(String)

  # Modern 2.0 back-reference relationship mapping
  user: Mapped["UserTable"] = relationship("UserTable", back_populates="tokens")

  @validates("token_type")
  def validate_token_type(self, key, value):
    allowed_values = [e.value for e in TokenTypeEnum]
    check_value = value.value if isinstance(value, TokenTypeEnum) else value

    if check_value not in allowed_values:
      raise ValueError(
        f"Error: Invalid token type: {value}. Must be one of {allowed_values}"
      )

    return check_value
