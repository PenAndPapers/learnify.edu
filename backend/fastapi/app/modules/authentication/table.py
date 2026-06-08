from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, validates

from app.database.session import Base

from .validation import TokenTypeEnum


class TokenTable(Base):
  __tablename__ = "tokens"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  token = Column(String, unique=True, nullable=False, index=True)
  token_type = Column(String, nullable=False, default=TokenTypeEnum.EMAIL_VERIFICATION)

  expires_at = Column(DateTime, nullable=False)
  is_revoked = Column(Boolean, server_default="false", nullable=False)

  user = relationship("UserTable", back_populates="tokens")

  @validates("token_type")
  def validate_token_type(self, key, value):
    # If it's an Enum instance, get its value; if it's already a string, validate it
    allowed_values = [e.value for e in TokenTypeEnum]

    check_value = value.value if isinstance(value, TokenTypeEnum) else value
    if check_value not in allowed_values:
      raise ValueError(f"Invalid token type: {value}. Must be one of {allowed_values}")

    return check_value
