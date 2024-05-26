class Course {
  final int courseId;
  final String courseTitle;
  final String url;
  final String summary;
  final int? numOfLecture;
  final int? numOfStud;
  final double? rate;
  final String? img;
  final String? instructor;
  final int? regPrice;
  final int? disPrice;
  final String updatedAt;
  final String createdAt;
  final int subcategoryId;
  final String subcategoryName;
  final int categoryId;
  final String categoryName;
  final int platformId;
  final String platformName;
  final List<String> tags;
  final List<String> reviewSummaries;

  Course({
    required this.courseId,
    required this.courseTitle,
    required this.url,
    required this.summary,
    this.numOfLecture,
    this.numOfStud,
    this.rate,
    this.img,
    this.instructor,
    this.regPrice,
    this.disPrice,
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
  });

  factory Course.fromJson(Map<String, dynamic> json) {
    return Course(
      courseId: json['course_id'],
      courseTitle: json['course_title'],
      url: json['url'],
      summary: json['summary'],
      numOfLecture: json['num_of_lecture'],
      numOfStud: json['num_of_stud'],
      rate: json['rate']?.toDouble(),
      img: json['img'],
      instructor: json['instructor'],
      regPrice: json['reg_price'],
      disPrice: json['dis_price'],
      updatedAt: json['updated_at'],
      createdAt: json['created_at'],
      subcategoryId: json['subcategory_id'],
      subcategoryName: json['subcategory_name'],
      categoryId: json['category_id'],
      categoryName: json['category_name'],
      platformId: json['platform_id'],
      platformName: json['platform_name'],
      tags: List<String>.from(json['tags']),
      reviewSummaries: List<String>.from(json['review_summaries']),
    );
  }
}