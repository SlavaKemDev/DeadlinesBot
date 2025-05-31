from typing import List

from sqlalchemy.orm import selectinload
from sqlalchemy import select

from .models import StudyProgram
from .session import AsyncSession


class StudyProgramService:
    @staticmethod
    async def get_list() -> List[StudyProgram]:
        async with AsyncSession() as session:
            result = await session.execute(
                select(StudyProgram).options(selectinload(StudyProgram.groups))
            )

            study_programs = result.scalars().all()

            return study_programs

    @staticmethod
    async def get_study_program(program_id: int) -> StudyProgram | None:
        async with AsyncSession() as session:
            result = await session.execute(
                select(StudyProgram)
                .where(StudyProgram.id == program_id)
                .options(selectinload(StudyProgram.groups))
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create_study_program(name: str) -> StudyProgram:
        async with AsyncSession() as session:
            study_program = StudyProgram(name=name)
            session.add(study_program)
            await session.commit()
            await session.refresh(study_program)
            return study_program
