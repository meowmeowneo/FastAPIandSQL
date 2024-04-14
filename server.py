from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import date
from sqlalchemy import Integer, String, Column, create_engine, DateTime, Date, select, func, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, registry, Mapped, mapped_column

app = FastAPI()

# SQLALCHEMY
engine = create_async_engine(
    "sqlite+aiosqlite:///OSport.db", connect_args={"check_same_thread": False})
SessionLocal = async_sessionmaker(engine)

# Описание класса USERS
class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(
                                DateTime(timezone = True),
                                default = func.now()
                            )
    
    updated: Mapped[DateTime] = mapped_column(
                                DateTime(timezone = True),
                                default = func.now(),
                                onupdate = func.now()
                            )

class Users(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(primary_key = True, unique = True)
    telegram_link: Mapped[str] = mapped_column(String(100), nullable = False)
    first_name: Mapped[str] = mapped_column(String(100), nullable = False)
    last_name: Mapped[str] = mapped_column(String(100), nullable = True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable = False)
    sex: Mapped[str] = mapped_column(String(1), nullable = False)

# PYDANTIC
class UserBase(BaseModel):
    telegram_id: int
    telegram_link: str
    first_name: str
    last_name: str
    birth_date: date
    sex: str
    # created: date
    # updated: date

# Подключение к БД и создание сессии
async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

# , response_model=UserBase - добавить в запрос, если необходимо возвращать данные определенного вида
# Добавление юзера в БД
@app.post('/userAdd')
async def add_user(user: UserBase, db: AsyncSession = Depends(get_db)):
    try:
        db_user = Users(**user.dict())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return "Пользователь добавлен :3"
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении пользователя: {str(e)}"}

# Получение пользователя
@app.post('/getUser')
async def get_user(telegram_id:int, db: AsyncSession = Depends(get_db)):
    try:
        results = await db.execute(select(Users).where(Users.telegram_id == telegram_id))
        user = results.scalars().all()
        return user
    except Exception as e:
        return {"error": f"Произошла ошибка при получении пользователя: {str(e)}"}

# Получение всех пользователей
@app.get('/getUsers')
async def get_users(db: AsyncSession = Depends(get_db)):
    try:
        results = await db.execute(select(Users))
        users = results.scalars().all()
        return {"users":users}
    except Exception as e:
        return {"error": f"Произошла ошибка при получении пользователей: {str(e)}"}
    
# Обновление ДР
@app.post('/updateBirthDate')
async def update_birth_date(telegram_id:int, new_birth_date:date, db: AsyncSession = Depends(get_db)):
    try:
        query = update(Users).where(Users.telegram_id == telegram_id).values(birth_date = new_birth_date)
        await db.execute(query)
        await db.commit()
        return "Дата рождения успешно обновлена!"
    except Exception as e:
        return {"error": f"Произошла ошибка при обновлении Др: {str(e)}"}

# Удаление пользователя из БД
@app.delete('/deleteUser')
async def delete_user(telegram_id:int, db: AsyncSession = Depends(get_db)):
    try:
        query = delete(Users).where(Users.telegram_id == telegram_id)
        await db.execute(query)
        await db.commit()
        return "Пользователь успешно удалён!"
    except Exception as e:
        return {"error": f"Произошла ошибка при удалении: {str(e)}"}
    
# Проверка на наличие в БД
@app.get('/chekUser')
async def chek_user(telegram_id:int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Users).where(Users.telegram_id == telegram_id)
        result = await db.execute(query)
        if result.first() is None:
            return False
        return True
    except Exception as e:
        return {"error": f"Произошла ошибка при удалении: {str(e)}"}
