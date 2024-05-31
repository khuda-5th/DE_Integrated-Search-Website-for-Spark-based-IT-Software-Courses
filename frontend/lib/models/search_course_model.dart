import 'package:lecture_web/models/base_course_model.dart';
import 'package:lecture_web/models/subsection_model.dart';

class SearchCourse implements BaseCourse {
  @override
  final int courseId;
  @override
  final String courseTitle;
  @override
  final String url;
  @override
  final String summary;
  @override
  final int? numOfLecture;
  @override
  final int? numOfStud;
  @override
  final double? rate;
  @override
  final String? img;
  @override
  final String? instructor;
  @override
  final int? regPrice;
  @override
  final int? disPrice;
  @override
  final int subcategoryId;
  @override
  final String subcategoryName;
  @override
  final int categoryId;
  @override
  final String categoryName;
  @override
  final int platformId;
  @override
  final String platformName;
  @override
  final List<String> tags;
  @override
  final List<String> reviewSummaries;
  @override
  final List<Section> sections;

  SearchCourse({
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

  factory SearchCourse.fromJson(Map<String, dynamic> json) {
    return SearchCourse(
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
      subcategoryId: json['subcategory_id'],
      subcategoryName: json['subcategory_name'],
      categoryId: json['category_id'],
      categoryName: json['category_name'],
      platformId: json['platform_id'],
      platformName: json['platform_name'],
      tags: List<String>.from(json['tags']),
      reviewSummaries: List<String>.from(json['review_summaries']),
      sections: (json['sections'] as List)
          .map((section) => Section.fromJson(section))
          .toList(),
    );
  }
}
