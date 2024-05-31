from fastapi import FastAPI, Depends, HTTPException, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import List, Dict
from app import models, crud, schemas
from app.database import engine, Base, get_db
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import sys
import os
from opensearch import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
router = APIRouter()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session


@router.get("/platforms", response_model=List[schemas.Platform])
async def read_platforms(db: AsyncSession = Depends(get_db)):
    platforms = await crud.get_platforms(db)
    return platforms


@router.get("/categories", response_model=List[schemas.Category])
async def read_categories(db: AsyncSession = Depends(get_db)):
    categories = await crud.get_categories(db)
    return categories


@router.get("/subcategories", response_model=List[schemas.Subcategory])
async def read_subcategories(db: AsyncSession = Depends(get_db)):
    subcategories = await crud.get_subcategories(db)
    return subcategories


@router.get("/courses_by_ids/", response_model=List[schemas.CourseResponse])
async def read_courses_by_ids(
    id: List[int] = Query(...), db: AsyncSession = Depends(get_db)
):
    courses = await crud.get_courses_by_ids(db, id)
    if not courses:
        raise HTTPException(status_code=404, detail="Courses not found")
    return courses


@router.get("/new_courses", response_model=List[schemas.NewCourse])
async def read_new_courses(db: AsyncSession = Depends(get_db)):
    new_courses = await crud.get_new_courses(db)
    return new_courses


@router.get("/courses_by_platform/", response_model=List[schemas.CourseResponse])
async def read_courses_by_platform(
    platform_name: str, db: AsyncSession = Depends(get_db)
):
    course_ids = await crud.get_course_ids_by_platform_name(db, platform_name)
    if not course_ids:
        raise HTTPException(status_code=404, detail="Courses not found")
    courses = await crud.get_courses_by_ids(db, course_ids)
    return courses


@router.get(
    "/subcategories_detail", response_model=List[schemas.SubcategoryDetailResponse]
)
async def read_subcategories_detail(db: AsyncSession = Depends(get_db)):
    result = await crud.get_subcategories_detail(db)
    return result


@router.get("/courses", response_model=schemas.CoursesResponse)
async def read_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await crud.get_courses(db, page, page_size)
    return result


@router.get("/search", response_model=List[schemas.CourseResponse])
async def search_opensearch(keyword: str, db: AsyncSession = Depends(get_db)):
    results = await search_all_platforms(keyword)

    # score 순으로 정렬
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)

    # url로 강의 id 조회
    course_ids = []
    for result in sorted_results:
        course_id = await crud.get_course_id_by_link(db, result["link"])
        if course_id is not None:
            course_ids.append(course_id)

    if not course_ids:
        raise HTTPException(status_code=404, detail="No courses found")

    # 강의 ID를 통해 강의 정보 조회
    courses = []
    for course_id in course_ids:
        course = await crud.get_course_by_id(db, course_id)
        courses.append(course)

    return courses


# @router.get("/search", response_model=List[schemas.CourseResponse])
# async def search_opensearch(keyword, db: AsyncSession = Depends(get_db)):

#     fastcampus_results = await search_fastcampus(keyword)
#     codeit_results = await search_codeit(keyword)
#     inflearn_results = await search_inflearn(keyword)

#     # 세 개 플랫폼 결과 합치기
#     results = fastcampus_results + codeit_results + inflearn_results

#     # score 순으로 정렬
#     sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)

#     # url로 강의 id 조회
#     course_ids = []
#     for result in sorted_results:
#         course_id = await crud.get_course_id_by_link(db, result["link"])
#         if course_id is not None:
#             course_ids.append(course_id)

#     if not course_ids:
#         raise HTTPException(status_code=404, detail="No courses found")

#     courses = await crud.get_courses_by_ids(db, course_ids)

#     return courses


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
