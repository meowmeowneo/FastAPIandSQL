from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import date
from sqlalchemy import desc, ForeignKey, null, and_, Integer, Text, String, Column, create_engine, DateTime, Date, select, func, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import relationship, sessionmaker, Session, DeclarativeBase, registry, Mapped, mapped_column

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
    



class Competitions(Base):
    __tablename__ = "competitions"

    competition_id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    title: Mapped[str] = mapped_column(String(100), nullable = False)
    password: Mapped[str] = mapped_column(Text, nullable = True)
    video_instruction: Mapped[str] = mapped_column(Text, nullable = False)

class CompetitionBase(BaseModel):
    title: str
    password: str
    video_instruction: str

# Добавление нового соревнования в БД
@app.post('/addCompetition')
async def add_competition(competition:CompetitionBase, db: AsyncSession = Depends(get_db)):
    try:
        db_competition=Competitions(**competition.dict())
        db.add(db_competition)
        await db.commit()
        await db.refresh(db_competition)
        return "Соревнование добавлено :3"
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Удаление определённого соревнования
@app.post('/deleteCompetition')
async def delete_competition(competition_id: int, db: AsyncSession = Depends(get_db)):
    try:
        del_from_competitions = delete(Competitions).where(Competitions.competition_id == competition_id)
        # del_from_results = delete(Results).where(Results.competition_id == competition_id)
        await db.execute(del_from_competitions)
        # await session.execute(del_from_results)
        await db.commit()
        return "Соревнование удалено :3"
    except Exception as e:
        return {"error": f"Произошла ошибка при удалении: {str(e)}"}

# Изменение определённого соревнования
@app.put('/editCompetition')
async def edit_competition(competition_id: int, competition:CompetitionBase, db: AsyncSession = Depends(get_db)):
    try:
        db_competition = await db.get(Competitions, competition_id)
        for field, value in competition.dict().items():
            setattr(db_competition, field, value)
        await db.commit()
        return "Соревнование обновлено :3"
    except Exception as e:
        return {"error": f"Произошла ошибка при обновлении: {str(e)}"}
    
# Выборка id первого соревнования в БД
@app.get('/getFirstId')
async def get_first_id(db: AsyncSession = Depends(get_db)):
    try:
        query = select(Competitions.competition_id)
        result = await db.execute(query)
        return result.scalar()
    except Exception as e:
        return {"error": f"Произошла ошибка при обновлении: {str(e)}"}

# Выборка определённого соревнования
@app.get('/getCompetition')
async def get_competition(competition_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Competitions).where(Competitions.competition_id == competition_id)
        result = await db.execute(query)
        return result.scalar()
    except Exception as e:
        return {"error": f"Произошла ошибка при обновлении: {str(e)}"}
    
# Выборка всех соревнований
@app.get('/getAllCompetition')
async def get_all_competition(db: AsyncSession = Depends(get_db)):
    try:
        query = select(Competitions)
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        return {"error": f"Произошла ошибка при обновлении: {str(e)}"}



class Results(Base):
    __tablename__ = "results"

    result_id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)

    competition_id: Mapped[int] = mapped_column(
        ForeignKey(Competitions.competition_id, ondelete = "CASCADE"),
        nullable = False
    )

    telegram_id: Mapped[int] = mapped_column(
        ForeignKey(Users.telegram_id, ondelete = "CASCADE"),
        nullable = False
    )
    
    video: Mapped[str] = mapped_column(Text, nullable = False)
    count: Mapped[int] = mapped_column(Integer, nullable = True)
    status: Mapped[str] = mapped_column(String(1), nullable = False)


    competition: Mapped["Competitions"] = relationship(
        backref = "results", foreign_keys = [competition_id], cascade = "all, delete"
    )
    
    user: Mapped["Users"] = relationship(
        backref = "results", foreign_keys = [telegram_id], cascade = "all, delete"
    )

class ResultsBase(BaseModel):
        competition_id: int
        telegram_id: int
        video: str
        count: int
        status: str

# Добавление результата в БД
@app.post('/addResult')
async def add_result(result:ResultsBase, db: AsyncSession = Depends(get_db)):
    try:
        db_result=Results(**result.dict())
        db.add(db_result)
        await db.commit()
        await db.refresh(db_result)
        return "Результат добавлен :3"
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Изменение результата в БД
@app.post('/editResult')
async def edit_result(competition_id: int, telegram_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    try:
        query = update(Results).where(and_(Results.competition_id == competition_id,Results.telegram_id == telegram_id)).values(video = data["video"],count = data["count"],status = data["status"])
        await db.execute(query)
        await db.commit()
        return "Результат изменен"
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Обнуление количества повторений
@app.post('/setNullResult')
async def set_null_result(result_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = update(Results).where(Results.result_id == result_id).values(count = None)
        await db.execute(query)
        await db.commit()
        return "Результат обнулен"
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Обнуление количества повторений
@app.post('/editCountResult')
async def edit_count_result(result_id: int, new_count: int, db: AsyncSession = Depends(get_db)):
    try:
        query = update(Results).where(Results.result_id == result_id).values(count = new_count, status = "✅")
        await db.execute(query)
        await db.commit()
        return "Результат повторений обновлен"
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Удаление результата пользователя
@app.delete('/deleteResult')
async def delete_result(result_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = delete(Results).where(Results.result_id == result_id)
        await db.execute(query)
        await db.commit()
        return "Результат удален"
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Выборка всех результатов определённого пользователя
@app.get('/getUserAll')
async def get_user_all(telegram_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Results).where(Results.telegram_id == telegram_id)
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Выборка результата пользователя по определённому соревнованию
@app.get('/getUserResult')
async def get_user_result(telegram_id: int, competition_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Results).where(and_(Results.telegram_id == telegram_id, Results.competition_id == competition_id))
        result = await db.execute(query)
        return result.scalar()
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Выборка всех результатов из БД
@app.get('/getAllResult')
async def get_all_result(db: AsyncSession = Depends(get_db)):
    try:
        query = select(Results)
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Выборка всех результатов определённого соревнования
@app.get('/getCompetitionResult')
async def get_competition_result(competition_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Results).where(Results.competition_id == competition_id)
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Выборка id всех участников определённого соревнования
@app.get('/getCompetitionMembers')
async def get_competition_Members(competition_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Results.telegram_id).where(Results.competition_id == competition_id)
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}

# Выборка статуса
@app.get('/chekStatus')
async def check_status(competition_id: int, telegram_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Results.status).where(and_(Results.competition_id == competition_id,Results.telegram_id == telegram_id))
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}

# Фильтрация результатов соревнования по count от большего к меньшему
@app.get('/raitingUsers')
async def rating_users(competition_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Results).where(Results.competition_id == competition_id).filter(Results.count != null()).order_by(desc(Results.count))
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
# Фильтрация результатов соревнования по count от большего к меньшему
@app.get('/totalRaitingUsers')
async def total_rating_users(db: AsyncSession = Depends(get_db)):
    try:
        query = select(Results.telegram_id, func.sum(Results.count).label('total_count')).filter(Results.status.isnot(None), Results.count > 0).group_by(Results.telegram_id).order_by(func.sum(Results.count).desc())
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        return {"error": f"Произошла ошибка при добавлении: {str(e)}"}
    
