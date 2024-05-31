from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date


class Platform(BaseModel):
    platform_id: int
    platform_name: str

    class Config:
        orm_mode = True


class Category(BaseModel):
    category_id: int
    category_name: str
    platform_id: int

    class Config:
        orm_mode = True


class Subcategory(BaseModel):
    subcategory_id: int
    subcategory_name: str
    category_id: int

    class Config:
        orm_mode = True


class CourseBase(BaseModel):
    course_title: str
    url: str
    num_of_lecture: Optional[int]
    num_of_stud: Optional[int]
    rate: Optional[float]
    img: Optional[str]
    instructor: Optional[str]
    reg_price: Optional[int]
    dis_price: Optional[int]
    subcategory_id: int
    subcategory_name: str
    category_id: int
    category_name: str
    platform_id: int
    platform_name: str

    class Config:
        orm_mode = True


class Course(CourseBase):
    course_id: int
    subcategory_id: int

    class Config:
        orm_mode = True


class SubsectionResponse(BaseModel):
    subsection_num: int
    subsection_name: str

    class Config:
        orm_mode = True


class SectionResponse(BaseModel):
    section_num: int
    section_name: str
    subsections: List[SubsectionResponse] = []

    class Config:
        orm_mode = True


class CourseResponse(BaseModel):
    course_id: int
    course_title: str
    url: str
    summary: str
    num_of_lecture: Optional[int]
    num_of_stud: Optional[int]
    rate: Optional[float]
    img: Optional[str]
    instructor: Optional[str]
    reg_price: Optional[int]
    dis_price: Optional[int]
    subcategory_id: Optional[int]
    subcategory_name: Optional[str]
    category_id: Optional[int]
    category_name: Optional[str]
    platform_id: Optional[int]
    platform_name: Optional[str]
    tags: List[str] = []
    review_summaries: List[str] = []
    sections: List[SectionResponse] = []

    class Config:
        orm_mode = True


class CoursesResponse(BaseModel):
    total: int
    courses: List[CourseResponse]

    class Config:
        orm_mode = True


class Tag(BaseModel):
    course_id: int
    tag: str

    class Config:
        orm_mode = True


class ReviewSummary(BaseModel):
    course_id: int
    summary: str

    class Config:
        orm_mode = True


class Section(BaseModel):
    course_id: int
    section_num: int
    section_name: Optional[str]
    num_of_lecture: Optional[int]
    running_time: Optional[str]

    class Config:
        orm_mode = True


class Subsection(BaseModel):
    subsection_id: int
    course_id: int
    subsection_num: int
    subsection_name: str
    section_num: int
    running_time: Optional[str]

    class Config:
        orm_mode = True


class NewCourse(BaseModel):
    course_id: int
    course_title: str
    subcategory_id: int
    url: str
    summary: str
    num_of_lecture: Optional[int]
    num_of_stud: Optional[int]
    rate: Optional[float]
    img: Optional[str]
    new_img: Optional[str]
    instructor: Optional[str]
    reg_price: Optional[int]
    dis_price: Optional[int]

    class Config:
        orm_mode = True


class SubcategoryDetailResponse(BaseModel):
    platform_id: int
    platform_name: str
    category_id: int
    category_name: str
    subcategory_id: int
    subcategory_name: str

    class Config:
        orm_mode = True


class SearchResult(BaseModel):
    link: str
    score: float
