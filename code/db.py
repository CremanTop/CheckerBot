import os.path
from typing import Final, NoReturn, Self, Any, Type, Optional

from sqlalchemy import create_engine, Engine, Column, Integer, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class User(Base):
    __tablename__: Final[str] = 'users'

    id = Column(Integer, primary_key=True)
    skins_unlocked = Column(Integer, default=0)
    choosen_skin = Column(String)
    win_count = Column(Integer, default=0)
    draw_count = Column(Integer, default=0)

    def __init__(self, user_id: int) -> NoReturn:
        self.id = user_id

    def __repr__(self) -> str:
        return f'Пользователь: [ID: {self.id}, Побед: {self.win_count}, Ничей: {self.draw_count}, Скин: {self.choosen_skin}, Открытые скины: {self.skins_unlocked}]'


class BotDB:
    """ОБЯЗАТЕЛЬНО ИСПОЛЬЗОВАТЬ ЧЕРЕЗ WITH!!!"""
    def __init__(self, db_file: str) -> None:
        self.__engine: Engine = create_engine(f'sqlite:///{db_file}')

        if not os.path.exists(db_file):
            self.create_db()

    def create_db(self) -> None:
        Base.metadata.create_all(self.__engine)

    def __enter__(self) -> Self:
        self.__session: Session = Session(bind=self.__engine)
        return self

    def __exit__(self, type_: Any, value: Any, traceback: Any) -> None:
        self.__session.commit()
        self.__session.close()

    def add_user(self, user_id: int) -> None:
        self.__session.add(User(user_id))

    def __get_user(self, user_id: int) -> Optional[User]:
        try:
            return self.__session.query(User).filter_by(id=user_id).one()
        except NoResultFound:
            return None

    def del_user(self, user_id: int) -> None:
        self.__session.delete(self.__get_user(user_id))

    def user_exists(self, user_id: int) -> bool:
        return self.__get_user(user_id) is not None

    def get_users(self) -> list[Type[User]]:
        return self.__session.query(User).all()

    @staticmethod
    def attrubyte_handler(fun):
        def handler(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except AttributeError:
                return None
        return handler

    @attrubyte_handler
    def get_skins(self, user_id: int) -> int:
        return self.__get_user(user_id).skins_unlocked

    @attrubyte_handler
    def get_choosen_skin(self, user_id: int) -> Optional[str]:
        return self.__get_user(user_id).choosen_skin

    @attrubyte_handler
    def get_wins(self, user_id: int) -> int:
        return self.__get_user(user_id).win_count

    @attrubyte_handler
    def get_draws(self, user_id: int) -> int:
        return self.__get_user(user_id).draw_count

    def set_skins(self, user_id: int, skins: int) -> None:
        self.__get_user(user_id).skins_unlocked = skins

    def win_increment(self, user_id: int) -> None:
        self.__get_user(user_id).win_count += 1

    def draw_increment(self, user_id: int) -> None:
        self.__get_user(user_id).draw_count += 1

    def set_choosen_skin(self, user_id: int, skin: str) -> None:
        self.__get_user(user_id).choosen_skin = skin
