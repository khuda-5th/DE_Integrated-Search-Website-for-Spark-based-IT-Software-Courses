from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join
from sqlalchemy.orm import joinedload
import app.models as models
import app.schemas as schemas
from sqlalchemy import func
from typing import List, Dict
from fastapi import HTTPException


async def get_platforms(db: AsyncSession):
    result = await db.execute(select(models.Platform))
    return result.scalars().all()


async def get_categories(db: AsyncSession):
    result = await db.execute(select(models.Category))
    return result.scalars().all()


async def get_subcategories(db: AsyncSession):
    result = await db.execute(select(models.Subcategory))
    return result.scalars().all()


async def get_courses(
    db: AsyncSession, page: int, page_size: int
) -> Dict[str, List[schemas.CourseResponse]]:
    offset = (page - 1) * page_size

    courses_stmt = (
        select(
            models.Course.course_id,
            models.Course.course_title,
            models.Course.url,
            models.Course.summary,
            models.Course.num_of_lecture,
            models.Course.num_of_stud,
            models.Course.rate,
            models.Course.img,
            models.Course.instructor,
            models.Course.reg_price,
            models.Course.dis_price,
            models.Subcategory.subcategory_id,
            models.Subcategory.subcategory_name,
            models.Category.category_id,
            models.Category.category_name,
            models.Platform.platform_id,
            models.Platform.platform_name,
        )
        .select_from(models.Course)
        .join(
            models.Subcategory,
            models.Course.subcategory_id == models.Subcategory.subcategory_id,
        )
        .join(
            models.Category,
            models.Subcategory.category_id == models.Category.category_id,
        )
        .join(
            models.Platform, models.Category.platform_id == models.Platform.platform_id
        )
        .offset(offset)
        .limit(page_size)
    )

    total_stmt = select(func.count(models.Course.course_id)).select_from(models.Course)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()

    courses_result = await db.execute(courses_stmt)
    courses = courses_result.all()

    course_responses = []
    for course in courses:
        # Get Tags
        tags_stmt = select(models.Tag.tag).where(
            models.Tag.course_id == course.course_id
        )
        tags_result = await db.execute(tags_stmt)
        tags = [tag for tag in tags_result.scalars().all()] or []

        # Get Review Summaries
        review_stmt = select(models.ReviewSummary.summary).where(
            models.ReviewSummary.course_id == course.course_id
        )
        review_result = await db.execute(review_stmt)
        reviews = [review for review in review_result.scalars().all()] or []

        # Get Sections and Subsections
        sections_stmt = (
            select(
                models.Section.section_num,
                models.Section.section_name,
                models.Subsection.subsection_num,
                models.Subsection.subsection_name,
            )
            .join(
                models.Subsection,
                (models.Section.course_id == models.Subsection.course_id)
                & (models.Section.section_num == models.Subsection.section_num),
            )
            .where(models.Section.course_id == course.course_id)
        )

        sections_result = await db.execute(sections_stmt)
        sections = {}
        for row in sections_result.all():
            section_num, section_name, subsection_num, subsection_name = row
            if section_num not in sections:
                sections[section_num] = {
                    "section_name": section_name,
                    "subsections": [],
                }
            sections[section_num]["subsections"].append(
                {"subsection_num": subsection_num, "subsection_name": subsection_name}
            )

        section_list = [
            {
                "section_num": section_num,
                "section_name": section["section_name"],
                "subsections": [
                    {
                        "subsection_num": s["subsection_num"],
                        "subsection_name": s["subsection_name"],
                    }
                    for s in section["subsections"]
                ],
            }
            for section_num, section in sections.items()
        ]

        course_responses.append(
            {
                "course_id": course.course_id,
                "course_title": course.course_title,
                "url": course.url,
                "summary": course.summary,
                "num_of_lecture": course.num_of_lecture,
                "num_of_stud": course.num_of_stud,
                "rate": course.rate,
                "img": course.img,
                "instructor": course.instructor,
                "reg_price": course.reg_price,
                "dis_price": course.dis_price,
                "subcategory_id": course.subcategory_id,
                "subcategory_name": course.subcategory_name,
                "category_id": course.category_id,
                "category_name": course.category_name,
                "platform_id": course.platform_id,
                "platform_name": course.platform_name,
                "tags": tags,
                "review_summaries": reviews,
                "sections": section_list,
            }
        )

    return {"total": total, "courses": course_responses}


async def get_courses_by_ids(db: AsyncSession, ids: List[int]):
    courses_stmt = (
        select(
            models.Course.course_id,
            models.Course.course_title,
            models.Course.url,
            models.Course.summary,
            models.Course.num_of_lecture,
            models.Course.num_of_stud,
            models.Course.rate,
            models.Course.img,
            models.Course.instructor,
            models.Course.reg_price,
            models.Course.dis_price,
            models.Subcategory.subcategory_id,
            models.Subcategory.subcategory_name,
            models.Category.category_id,
            models.Category.category_name,
            models.Platform.platform_id,
            models.Platform.platform_name,
        )
        .select_from(models.Course)
        .join(
            models.Subcategory,
            models.Course.subcategory_id == models.Subcategory.subcategory_id,
        )
        .join(
            models.Category,
            models.Subcategory.category_id == models.Category.category_id,
        )
        .join(
            models.Platform, models.Category.platform_id == models.Platform.platform_id
        )
        .where(models.Course.course_id.in_(ids))
    )

    courses_result = await db.execute(courses_stmt)
    courses = courses_result.all()

    course_responses = []
    for course in courses:
        # Get Tags
        tags_stmt = select(models.Tag.tag).where(
            models.Tag.course_id == course.course_id
        )
        tags_result = await db.execute(tags_stmt)
        tags = [tag for tag in tags_result.scalars().all()] or []

        # Get Review Summaries
        review_stmt = select(models.ReviewSummary.summary).where(
            models.ReviewSummary.course_id == course.course_id
        )
        review_result = await db.execute(review_stmt)
        reviews = [review for review in review_result.scalars().all()] or []

        # Get Sections and Subsections
        sections_stmt = (
            select(
                models.Section.section_num,
                models.Section.section_name,
                models.Subsection.subsection_num,
                models.Subsection.subsection_name,
            )
            .join(
                models.Subsection,
                (models.Section.course_id == models.Subsection.course_id)
                & (models.Section.section_num == models.Subsection.section_num),
            )
            .where(models.Section.course_id == course.course_id)
        )

        sections_result = await db.execute(sections_stmt)
        sections = {}
        for row in sections_result.all():
            section_num, section_name, subsection_num, subsection_name = row
            if section_num not in sections:
                sections[section_num] = {
                    "section_name": section_name,
                    "subsections": [],
                }
            sections[section_num]["subsections"].append(
                {"subsection_num": subsection_num, "subsection_name": subsection_name}
            )
        section_list = [
            {
                "section_num": section_num,
                "section_name": section["section_name"],
                "subsections": [
                    {
                        "subsection_num": s["subsection_num"],
                        "subsection_name": s["subsection_name"],
                    }
                    for s in section["subsections"]
                ],
            }
            for section_num, section in sections.items()
        ]

        course_responses.append(
            {
                "course_id": course.course_id,
                "course_title": course.course_title,
                "url": course.url,
                "summary": course.summary,
                "num_of_lecture": course.num_of_lecture,
                "num_of_stud": course.num_of_stud,
                "rate": course.rate,
                "img": course.img,
                "instructor": course.instructor,
                "reg_price": course.reg_price,
                "dis_price": course.dis_price,
                "subcategory_id": course.subcategory_id,
                "subcategory_name": course.subcategory_name,
                "category_id": course.category_id,
                "category_name": course.category_name,
                "platform_id": course.platform_id,
                "platform_name": course.platform_name,
                "tags": tags,
                "review_summaries": reviews,
                "sections": section_list,
            }
        )

    return course_responses


async def get_course_ids_by_platform_name(db: AsyncSession, platform_name: str):
    course_ids = await db.execute(
        select(models.Course.course_id)
        .join(models.Subcategory)
        .join(models.Category)
        .join(models.Platform)
        .where(models.Platform.platform_name == platform_name)
    )

    course_ids = [course_id.course_id for course_id in course_ids.scalars()]
    return course_ids


async def get_subcategories_detail(db: AsyncSession):
    stmt = (
        select(
            models.Platform.platform_id,
            models.Platform.platform_name,
            models.Category.category_id,
            models.Category.category_name,
            models.Subcategory.subcategory_id,
            models.Subcategory.subcategory_name,
        )
        .select_from(models.Subcategory)
        .join(
            models.Category,
            models.Subcategory.category_id == models.Category.category_id,
        )
        .join(
            models.Platform, models.Category.platform_id == models.Platform.platform_id
        )
    )

    result = await db.execute(stmt)
    subcategories_detail = result.all()

    subcategories_response = []
    for subcategory in subcategories_detail:
        subcategories_response.append(
            {
                "platform_id": subcategory.platform_id,
                "platform_name": subcategory.platform_name,
                "category_id": subcategory.category_id,
                "category_name": subcategory.category_name,
                "subcategory_id": subcategory.subcategory_id,
                "subcategory_name": subcategory.subcategory_name,
            }
        )

    return subcategories_response


async def get_course_id_by_link(db: AsyncSession, link: str) -> int:
    result = await db.execute(
        select(models.Course.course_id).where(models.Course.url == link)
    )
    course_id = result.scalar()
    return course_id


async def get_course_by_id(db: AsyncSession, course_id: int) -> schemas.CourseResponse:
    courses_stmt = (
        select(
            models.Course.course_id,
            models.Course.course_title,
            models.Course.url,
            models.Course.summary,
            models.Course.num_of_lecture,
            models.Course.num_of_stud,
            models.Course.rate,
            models.Course.img,
            models.Course.instructor,
            models.Course.reg_price,
            models.Course.dis_price,
            models.Subcategory.subcategory_id,
            models.Subcategory.subcategory_name,
            models.Category.category_id,
            models.Category.category_name,
            models.Platform.platform_id,
            models.Platform.platform_name,
        )
        .select_from(models.Course)
        .join(
            models.Subcategory,
            models.Course.subcategory_id == models.Subcategory.subcategory_id,
        )
        .join(
            models.Category,
            models.Subcategory.category_id == models.Category.category_id,
        )
        .join(
            models.Platform, models.Category.platform_id == models.Platform.platform_id
        )
        .where(models.Course.course_id == course_id)
    )

    courses_result = await db.execute(courses_stmt)
    course = courses_result.first()

    if course:
        # Get Tags
        tags_stmt = select(models.Tag.tag).where(
            models.Tag.course_id == course.course_id
        )
        tags_result = await db.execute(tags_stmt)
        tags = [tag for tag in tags_result.scalars().all()] or []

        # Get Review Summaries
        review_stmt = select(models.ReviewSummary.summary).where(
            models.ReviewSummary.course_id == course.course_id
        )
        review_result = await db.execute(review_stmt)
        reviews = [review for review in review_result.scalars().all()] or []

        # Get Sections and Subsections
        sections_stmt = (
            select(
                models.Section.section_num,
                models.Section.section_name,
                models.Subsection.subsection_num,
                models.Subsection.subsection_name,
            )
            .join(
                models.Subsection,
                (models.Section.course_id == models.Subsection.course_id)
                & (models.Section.section_num == models.Subsection.section_num),
            )
            .where(models.Section.course_id == course.course_id)
        )

        sections_result = await db.execute(sections_stmt)
        sections = {}
        for row in sections_result.all():
            section_num, section_name, subsection_num, subsection_name = row
            if section_num not in sections:
                sections[section_num] = {
                    "section_name": section_name,
                    "subsections": [],
                }
            sections[section_num]["subsections"].append(
                {"subsection_num": subsection_num, "subsection_name": subsection_name}
            )

        section_list = [
            {
                "section_num": section_num,
                "section_name": section["section_name"],
                "subsections": [
                    {
                        "subsection_num": s["subsection_num"],
                        "subsection_name": s["subsection_name"],
                    }
                    for s in section["subsections"]
                ],
            }
            for section_num, section in sections.items()
        ]

        return schemas.CourseResponse(
            course_id=course.course_id,
            course_title=course.course_title,
            url=course.url,
            summary=course.summary,
            num_of_lecture=course.num_of_lecture,
            num_of_stud=course.num_of_stud,
            rate=course.rate,
            img=course.img,
            instructor=course.instructor,
            reg_price=course.reg_price,
            dis_price=course.dis_price,
            subcategory_id=course.subcategory_id,
            subcategory_name=course.subcategory_name,
            category_id=course.category_id,
            category_name=course.category_name,
            platform_id=course.platform_id,
            platform_name=course.platform_name,
            tags=tags,
            review_summaries=reviews,
            sections=section_list,
        )

    raise HTTPException(status_code=404, detail="Course not found")
