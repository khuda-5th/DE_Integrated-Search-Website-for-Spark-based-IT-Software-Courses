import 'package:lecture_web/models/base_course_model.dart';
import '../models/course_model.dart';

List<Course> filterLectures({
  required List<BaseCourse> allLectures,
  required List<String> selectedHorizontalCategories,
  required List<String> selectedCategories,
}) {
  List<String> subcategoryNames =
      selectedHorizontalCategories.expand((category) {
    return getSubcategoriesForCategory(category);
  }).toList();

  List<String> categoryNames = selectedHorizontalCategories.expand((category) {
    return getCategoriesForCategory(category);
  }).toList();

  print('Selected Subcategories: $subcategoryNames');
  print('Selected Categories: $categoryNames');

  List<Course> lecturesToFilter = List.from(allLectures);

  if (subcategoryNames.isNotEmpty || categoryNames.isNotEmpty) {
    lecturesToFilter = lecturesToFilter.where((lecture) {
      bool matchesSubcategory = subcategoryNames.isEmpty ||
          subcategoryNames.contains(lecture.subcategoryName);
      bool matchesCategory =
          categoryNames.isEmpty || categoryNames.contains(lecture.categoryName);
      return matchesSubcategory || matchesCategory;
    }).toList();
  }

  if (selectedCategories.contains('낮은 가격순')) {
    lecturesToFilter.sort((a, b) {
      num priceA = a.disPrice ?? a.regPrice ?? double.infinity;
      num priceB = b.disPrice ?? b.regPrice ?? double.infinity;
      if (priceA == double.infinity && priceB == double.infinity) return 0;
      if (priceA == double.infinity) return 1;
      if (priceB == double.infinity) return -1;
      return priceA.compareTo(priceB);
    });
  } else if (selectedCategories.contains('높은 가격순')) {
    lecturesToFilter.sort((a, b) {
      num priceA = a.disPrice ?? a.regPrice ?? -double.infinity;
      num priceB = b.disPrice ?? b.regPrice ?? -double.infinity;
      if (priceA == -double.infinity && priceB == -double.infinity) return 0;
      if (priceA == -double.infinity) return 1;
      if (priceB == -double.infinity) return -1;
      return priceB.compareTo(priceA);
    });
  }

  print('Filtered Lectures: ${lecturesToFilter.length}');
  return lecturesToFilter;
}

List<String> getSubcategoriesForCategory(String category) {
  switch (category) {
    case '프론트엔드':
      return ['프론트엔드', '프론트엔드 개발', '웹 개발', '웹 퍼블리싱'];
    case '백엔드':
      return ['데이터베이스', '백엔드', '백엔드 개발', '풀스택', '웹 개발'];
    case '모바일 앱':
      return ['모바일 앱 개발', '데스크톱 앱 개발'];
    case '데브옵스 · 인프라':
      return ['데브옵스 · 인프라', 'DevOps/Infra'];
    case '데이터 사이언스':
      return ['데이터 분석', '데이터엔지니어링', '데이터 사이언스'];
    case '인공지능':
      return ['인공 지능', '머신러닝'];
    case '게임 개발':
      return ['게임 개발'];
    case '컴퓨터 사이언스':
      return ['알고리즘 · 자료구조', '프로그래밍 언어', '블록체인 개발', '컴퓨터 공학/SW 엔지니어링'];
    case '디자인':
      return ['디자인', '일러스트'];
    case '기타':
      return [
        '기타 (개발 · 프로그래밍)',
        '개발 도구',
        '소프트웨어 테스트',
        'VR/AR',
        '자격증 (개발 · 프로그래밍)',
        '업무 자동화',
        'IT 교양'
      ];
    default:
      return [];
  }
}

List<String> getCategoriesForCategory(String category) {
  switch (category) {
    case '데브옵스 · 인프라':
      return ['보안 · 네트워크'];
    case '데이터 사이언스':
      return ['데이터 사이언스'];
    case '인공지능':
      return ['인공지능'];
    case '게임 개발':
      return ['게임 개발'];
    case '컴퓨터 사이언스':
      return ['하드웨어', '프로그래밍 언어', '컴퓨터 사이언스'];
    case '디자인':
      return ['디자인', '일러스트'];
    case '기타':
      return [
        '커리어',
        '비즈니스 · 마케팅',
        '자기계발',
        '학문 · 외국어',
        '비즈니스/기획',
        '영상/3D',
        '금융/투자',
        '업무 생산성',
        '마케팅'
      ];
    default:
      return [];
  }
}
