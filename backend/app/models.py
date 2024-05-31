from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Integer,
    String,
    Date,
    ForeignKey,
    CheckConstraint,
    Interval,
    DECIMAL,
    CHAR,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Platform(Base):
    __tablename__ = "platform"
    platform_id = Column(
        Integer,
        CheckConstraint("platform_id IN (1, 2, 3, 4, 5)"),
        primary_key=True,
        autoincrement=True,
    )
    platform_name = Column(
        CHAR(10),
        CheckConstraint(
            "platform_name IN ('inflearn', 'fastcampus', 'codeit', 'capple', 'naver')"
        ),
        nullable=False,
    )


class Category(Base):
    __tablename__ = "category"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(20), nullable=False)
    platform_id = Column(Integer, ForeignKey("platform.platform_id"), nullable=False)
    platform = relationship("Platform")


class Subcategory(Base):
    __tablename__ = "subcategory"
    subcategory_id = Column(Integer, primary_key=True, autoincrement=True)
    subcategory_name = Column(String(40), nullable=False)
    category_id = Column(Integer, ForeignKey("category.category_id"), nullable=False)
    category = relationship("Category")


class Course(Base):
    __tablename__ = "course"
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    course_title = Column(String(200), nullable=False)
    subcategory_id = Column(
        Integer, ForeignKey("subcategory.subcategory_id"), nullable=False
    )
    url = Column(String(250), unique=True, nullable=False)
    summary = Column(String(350), nullable=False)
    num_of_lecture = Column(Integer, CheckConstraint("num_of_lecture >= 0"))
    num_of_stud = Column(Integer, CheckConstraint("num_of_stud >= 0"))
    rate = Column(DECIMAL, CheckConstraint("rate >= 0"))
    img = Column(String(150), nullable=False)
    instructor = Column(String(40))
    reg_price = Column(Integer, CheckConstraint("reg_price >= 0"))
    dis_price = Column(Integer, CheckConstraint("dis_price >= 0"))
    updated_at = Column(Date, nullable=False)
    created_at = Column(Date, nullable=False)
    subcategory = relationship("Subcategory")


class Tag(Base):
    __tablename__ = "tag"
    course_id = Column(Integer, ForeignKey("course.course_id"), primary_key=True)
    tag = Column(String(30), primary_key=True)
    updated_at = Column(Date, nullable=False)
    created_at = Column(Date, nullable=False)


class ReviewSummary(Base):
    __tablename__ = "review_summary"
    course_id = Column(Integer, ForeignKey("course.course_id"), primary_key=True)
    summary = Column(String(150), primary_key=True)
    updated_at = Column(Date, nullable=False)
    created_at = Column(Date, nullable=False)


class Section(Base):
    __tablename__ = "section"
    course_id = Column(Integer, ForeignKey("course.course_id"), primary_key=True)
    section_num = Column(Integer, primary_key=True)
    section_name = Column(String(200))
    num_of_lecture = Column(Integer, CheckConstraint("num_of_lecture >= 0"))
    running_time = Column(Interval)
    updated_at = Column(Date, nullable=False)
    created_at = Column(Date, nullable=False)


class Subsection(Base):
    __tablename__ = "subsection"
    subsection_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course.course_id"), nullable=False)
    subsection_num = Column(
        Integer, CheckConstraint("subsection_num >= 0"), nullable=False
    )
    subsection_name = Column(String(100), nullable=False)
    section_num = Column(Integer, nullable=False)
    running_time = Column(Interval)
    updated_at = Column(Date, nullable=False)
    created_at = Column(Date, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ["course_id", "section_num"],
            ["section.course_id", "section.section_num"],
        ),
    )


class NewCourse(Base):
    __tablename__ = "new_course"
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    course_title = Column(String(200), nullable=False)
    subcategory_id = Column(
        Integer, ForeignKey("subcategory.subcategory_id"), nullable=False
    )
    url = Column(String(250), unique=True, nullable=False)
    summary = Column(String(350), nullable=False)
    num_of_lecture = Column(Integer, CheckConstraint("num_of_lecture >= 0"))
    num_of_stud = Column(Integer, CheckConstraint("num_of_stud >= 0"))
    rate = Column(DECIMAL, CheckConstraint("rate >= 0"))
    img = Column(String(150), nullable=False)
    new_img = Column(String(150))
    instructor = Column(String(40))
    reg_price = Column(Integer, CheckConstraint("reg_price >= 0"))
    dis_price = Column(Integer, CheckConstraint("dis_price >= 0"))
    updated_at = Column(Date, nullable=False)
    created_at = Column(Date, nullable=False)
