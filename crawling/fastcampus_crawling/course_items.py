class FastcampusItem:
    def __init__(self, categories=None):
        self.categories = categories if categories is not None else []

    def to_dict(self):
        return {"categories": [category.to_dict() for category in self.categories]}


class CategoryItem:
    def __init__(self, category_name=None, sub_categories=None):
        self.category_name = category_name
        self.sub_categories = sub_categories if sub_categories is not None else []

    def to_dict(self):
        return {
            "category_name": self.category_name,
            "sub_categories": [
                sub_category.to_dict() for sub_category in self.sub_categories
            ],
        }


class SubCategoryItem:
    def __init__(self, sub_category_name=None, courses=None):
        self.sub_category_name = sub_category_name
        self.courses = courses if courses is not None else []

    def to_dict(self):
        return {
            "sub_category_name": self.sub_category_name,
            "courses": [course.to_dict() for course in self.courses],
        }


class CourseItem:
    def __init__(
        self,
        title=None,
        intro=None,
        badge=None,
        tags=None,
        course_img=None,
        course_url=None,
        regular_price=None,
        sale_price=None,
        summary=None,
        parts=None,
        accordion=None,
    ):
        self.title = title
        self.intro = intro
        self.badge = badge
        self.tags = tags if tags is not None else []
        self.course_img = course_img
        self.course_url = course_url
        self.regular_price = regular_price
        self.sale_price = sale_price
        self.summary = summary if summary is not None else []
        self.parts = parts if parts is not None else []
        self.accordion = accordion if accordion is not None else []

    def to_dict(self):
        return {
            "title": self.title,
            "intro": self.intro,
            "badge": self.badge,
            "tags": self.tags,
            "course_img": self.course_img,
            "course_url": self.course_url,
            "regular_price": self.regular_price,
            "sale_price": self.sale_price,
            "summary": self.summary,
            "parts": self.parts,
            "accordion": self.accordion,
        }


class NewCourseItems:
    def __init__(self, new_courses=None):
        self.new_courses = new_courses if new_courses is not None else []

    def to_dict(self):
        return {"new_courses": [course.to_dict() for course in self.new_courses]}
