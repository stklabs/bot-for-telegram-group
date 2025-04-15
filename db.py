from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.expression import func


engine = create_engine("sqlite:////data/bot_sats_lottu.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    ln_address = Column(String, nullable=False)
    check_in = Column(Boolean, nullable=False, default=False)


def create_tables():
    Base.metadata.create_all(bind=engine)


def save_ln_address(user_id: int, username: str, ln_address: str):
    session = SessionLocal()
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        user.ln_address = ln_address
    else:
        user = User(user_id=user_id, username=username, ln_address=ln_address)
        session.add(user)
    session.commit()
    session.close()


def get_ln_address(user_id: int):
    session = SessionLocal()
    user = session.query(User).filter_by(user_id=user_id).first()
    session.close()
    return user.ln_address if user else None


def get_random_ln_address():
    session = SessionLocal()
    result = session.query(User.ln_address).filter(
        User.check_in.is_(True)
    ).order_by(func.random()).first()
    session.close()
    return result.ln_address if result else None


def check_in(user_id: int):
    session = SessionLocal()
    if user := session.query(User).filter_by(user_id=user_id).first():
        user.check_in = True
        session.commit()
    session.close()


def is_checked(user_id: int) -> bool | None:
    session = SessionLocal()
    user = session.query(User).filter_by(user_id=user_id).first()
    session.close()
    return user.check_in if user else None


def clear_checkins():
    session = SessionLocal()
    session.query(User).update({User.check_in: False})
    session.commit()
    session.close()


def count_checkins():
    session = SessionLocal()
    total = session.query(User).filter(User.check_in.is_(True)).count()
    session.close()
    return total


def get_username_ln_address_total_check_in() -> tuple[str, str, int] | None:
    session = SessionLocal()
    result = session.query(User).filter(
        User.check_in.is_(True)
    ).order_by(func.random()).first()
    total = session.query(User).filter(User.check_in.is_(True)).count()
    session.close()
    if result:
        return str(result.ln_address), str(result.username), total
    return None


create_tables()
