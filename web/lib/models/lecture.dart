class Lecture {
  final int courseId;
  final String courseTitle;
  final String url;
  final String summary;
  final int? numOfLecture;
  final int? numOfStud;
  final double? rate;
  final String img;
  final String instructor;
  final int regPrice;
  final int disPrice;
  final DateTime updatedAt;
  final DateTime createdAt;
  final int subcategoryId;
  final String subcategoryName;
  final int categoryId;
  final String categoryName;
  final int platformId;
  final String platformName;
  final List<String> tags;
  final Map<String, dynamic> reviewSummaries;
  final Map<String, dynamic> sections;

  Lecture({
    required this.courseId,
    required this.courseTitle,
    required this.url,
    required this.summary,
    this.numOfLecture,
    this.numOfStud,
    this.rate,
    required this.img,
    required this.instructor,
    required this.regPrice,
    required this.disPrice,
    required this.updatedAt,
    required this.createdAt,
    required this.subcategoryId,
    required this.subcategoryName,
    required this.categoryId,
    required this.categoryName,
    required this.platformId,
    required this.platformName,
    required this.tags,
    required this.reviewSummaries,
    required this.sections,
  });

  factory Lecture.fromJson(Map<String, dynamic> json) {
    return Lecture(
      courseId: json['course_id'],
      courseTitle: json['course_title'],
      url: json['url'],
      summary: json['summary'],
      numOfLecture: json['num_of_lecture'],
      numOfStud: json['num_of_stud'],
      rate: json['rate'] != null ? json['rate'].toDouble() : null,
      img: json['img'],
      instructor: json['instructor'] ?? '',
      regPrice: json['reg_price'],
      disPrice: json['dis_price'],
      updatedAt: DateTime.parse(json['updated_at']),
      createdAt: DateTime.parse(json['created_at']),
      subcategoryId: json['subcategory_id'],
      subcategoryName: json['subcategory_name'],
      categoryId: json['category_id'],
      categoryName: json['category_name'],
      platformId: json['platform_id'],
      platformName: json['platform_name'],
      tags: List<String>.from(json['tags']),
      reviewSummaries: json['review_summaries'],
      sections: json['sections'],
    );
  }
}
