import 'package:lecture_web/models/subsection_model.dart';

abstract class BaseCourse {
  int get courseId;
  String get courseTitle;
  String get url;
  String get summary;
  int? get numOfLecture;
  int? get numOfStud;
  double? get rate;
  String? get img;
  String? get instructor;
  int? get regPrice;
  int? get disPrice;
  int get subcategoryId;
  String get subcategoryName;
  int get categoryId;
  String get categoryName;
  int get platformId;
  String get platformName;
  List<String> get tags;
  List<String> get reviewSummaries;
  List<Section> get sections;
}
