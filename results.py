# results.py

# Сторонние модули
from sqlalchemy import select, delete, update, and_, desc, null, func
from sqlalchemy.ext.asyncio import AsyncSession

# Созданные модули
from database.models import Results


# Добавление результата в БД
async def add(session: AsyncSession, data: dict):
    result = Results(
        competition_id = data["competition_id"],
        telegram_id = data["telegram_id"],
        video = data["video"],
        count = data["count"],
        status = data["status"]
    )

    session.add(result)
    await session.commit()


# Изменение результата юзера по определённому соревнованию
async def edit(session: AsyncSession, competition_id: int, telegram_id: int, data: dict):
    query = update(Results).where(
        and_(
            Results.competition_id == competition_id,
            Results.telegram_id == telegram_id
        )
    ).values(
        video = data["video"],
        count = data["count"],
        status = data["status"]
    )

    await session.execute(query)
    await session.commit()


# Обнуление количества повторений
async def set_null_count(session: AsyncSession, result_id: int):
    query = update(Results).where(
        Results.result_id == result_id).values(count = None)
    
    await session.execute(query)
    await session.commit()


# Изменяем количество повторений
async def edit_count(session: AsyncSession, result_id: int, new_count: int):
    query = update(Results).where(
        Results.result_id == result_id).values(
            count = new_count, status = "✅"
        )
    
    await session.execute(query)
    await session.commit()


# Удаление результата юзера
async def delete_res(session: AsyncSession, result_id: int):
    query = delete(Results).where(Results.result_id == result_id)
    await session.execute(query)
    await session.commit()


# Выборка всех результатов определённого юзера
async def get_user_all(session: AsyncSession, telegram_id: int):
    query = select(Results).where(Results.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalars().all()


# Выборка результата юзера по определённому соревнованию
async def get_user(session: AsyncSession, competition_id: int, telegram_id: int):
    query = select(Results).where(
        and_(
            Results.competition_id == competition_id,
            Results.telegram_id == telegram_id
        )
    )

    result = await session.execute(query)
    return result.scalar()


# Выборка всех результатов из БД
async def get_all(session: AsyncSession):
    query = select(Results)
    result = await session.execute(query)
    return result.scalars().all()


# Выборка всех результатов определённого соревнования
async def get_competition(session: AsyncSession, competition_id: int):
    query = select(Results).where(Results.competition_id == competition_id)
    result = await session.execute(query)
    return result.scalars().all()


# Выборка id всех участников определённого соревнования
async def competition_members(session: AsyncSession, competition_id: int):
    query = select(Results.telegram_id).where(
        Results.competition_id == competition_id
    )

    result = await session.execute(query)
    return result.scalars().all()


# Выборка статуса
async def check_status(session: AsyncSession, competition_id: int, telegram_id: int):
    query = select(Results.status).where(
        and_(
            Results.competition_id == competition_id,
            Results.telegram_id == telegram_id
        )
    )

    result = await session.execute(query)
    return result.scalar()


# Фильтрация результатов соревнования по count от большего к меньшему
async def rating_users(session: AsyncSession, competition_id: int):
    query = select(Results).where(
        Results.competition_id == competition_id
    ).filter(Results.count != null()).order_by(desc(Results.count))

    result = await session.execute(query)
    return result.scalars().all()

# Глобальный рейтинг по всем пользователям.
async def total_rating_users(session: AsyncSession):
    query = select(
    Results.telegram_id,
    func.sum(Results.count).label('total_count')
    ).filter(
    Results.status.isnot(None), Results.count > 0
    ).group_by(
    Results.telegram_id
    ).order_by(
    func.sum(Results.count).desc()
    )
    result = await session.execute(query)
    return result.all()

