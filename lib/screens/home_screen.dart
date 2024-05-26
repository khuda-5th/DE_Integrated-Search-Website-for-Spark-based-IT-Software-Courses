import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../widgets/horizontal_category_button.dart';
import '../models/course_model.dart';
import '../widgets/course_list.dart';
import '../services/url_launcher_service.dart';
import '../utils/constants.dart';
import 'lecture_details_screen.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Course> allLectures = []; // 서버에서 받아온 모든 강의를 저장하는 리스트
  List<Course> filteredLectures = []; // 선택한 카테고리나 검색어에 따라 필터링된 강의들을 저장하는 리스트
  List<String> selectedHorizontalCategories = []; // 선택한 가로 카테고리들을 저장하는 리스트

  @override
  void initState() {
    // 위젯이 처음 생성될 때 호출
    super.initState();
    loadData();
  }

  // 서버에서 데이터를 가져오는 함수
  Future<void> loadData() async {
    final response = await http.get(Uri.parse(API_BASE_URL)); // 실제 API URL로 변경

    if (response.statusCode == 200) {
      List<Course> courses =
          parseCourses(response.body); // json을 Course 객체 리스트로 변환

      // 디버그 프린트를 통해 받아온 데이터를 확인
      print('로드한 강의들: ${courses.map((c) => c.courseTitle).toList()}');

      setState(() {
        // 강의들이 갱신됨
        allLectures = courses; // 모든 강의
        filteredLectures = courses; // 필터링된 강의
      });
    } else {
      throw Exception('강의 로드 실패');
    }
  }

  // 파싱 함수
  List<Course> parseCourses(String responseBody) {
    final parsed = json.decode(responseBody).cast<Map<String, dynamic>>();
    List<Course> courses =
        parsed.map<Course>((json) => Course.fromJson(json)).toList();
    print('파싱된 강의: ${courses.map((c) => c.courseTitle).toList()}');
    return courses;
  }

  // 버튼 클릭시 바로 호출되는 함수
  void toggleHorizontalCategory(String horizontalCategory) {
    setState(() {
      if (selectedHorizontalCategories.contains(horizontalCategory)) {
        selectedHorizontalCategories.remove(horizontalCategory);
      } else {
        selectedHorizontalCategories.add(horizontalCategory);
      }
      print('선택된 카테고리 목록: $selectedHorizontalCategories');
      filterLectures(); // 선택된 카테고리에 따라 강의 목록 필터링
    });
  }

  // 선택한 카테고리에 따라 강의를 필터링
  void filterLectures() {
    print('필터링 함수 호출');
    if (selectedHorizontalCategories.isEmpty) {
      setState(() {
        filteredLectures = allLectures;
        print('아무 카테고리도 선택 안됨');
      });
    } else {
      setState(() {
        filteredLectures = allLectures.where((course) {
          bool matchesCategory = false;

          print(
              '현재 강의: ${course.courseTitle}, subcategoryName: ${course.subcategoryName}, categoryName: ${course.categoryName}, platformName: ${course.platformName}');

          if (selectedHorizontalCategories.contains('프론트엔드') &&
              (course.subcategoryName == "프론트엔드" ||
                  course.subcategoryName == "개발 도구" ||
                  course.subcategoryName == "IT 교양")) {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('백엔드') &&
              (course.subcategoryName == "백엔드" ||
                  course.subcategoryName == "개발 도구" ||
                  course.subcategoryName == "IT 교양")) {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('모바일 앱') &&
              (course.subcategoryName == "모바일 앱" ||
                  course.subcategoryName == "개발 도구" ||
                  course.subcategoryName == "IT 교양")) {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('데브옵스 · 인프라') &&
              (course.subcategoryName == "데브옵스 · 인프라" ||
                  course.subcategoryName == "개발 도구" ||
                  course.subcategoryName == "IT 교양")) {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('데이터 사이언스') &&
              (course.subcategoryName == '데이터 분석' ||
                  course.categoryName == '데이터 사이언스')) {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('인공지능') &&
              (course.subcategoryName == '인공 지능' ||
                  course.categoryName == '인공 지능')) {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('컴퓨터 사이언스') &&
              (course.categoryName == "프로그래밍 언어" ||
                  course.categoryName == "컴퓨터 사이언스")) {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('게임 개발') &&
              ((course.platformId == 1 && course.categoryName == '게임 개발') ||
                  (course.platformId == 2 &&
                      course.subcategoryName == '게임 개발'))) {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('디자인') &&
              course.subcategoryName == "디자인") {
            matchesCategory = true;
          }

          if (selectedHorizontalCategories.contains('기타') &&
              (course.subcategoryName == "업무 자동화" ||
                  course.subcategoryName == "개발 도구" ||
                  course.subcategoryName == "IT 교양")) {
            matchesCategory = true;
          }

          if (matchesCategory) {
            print('필터링된 강의들: ${course.courseTitle}');
          }

          return matchesCategory;
        }).toList();
        print(
            '필터된 강의들의 개수: ${filteredLectures.length}'); // 조건에 맞는 강의들이 filteredLectures 리스트에 저장
      });
    }
  }

  // 검색어 입력할 때, 필터링된 강의를 보여줌
  void searchLectures(String query) {
    setState(() {
      if (query.isEmpty) {
        filterLectures();
      } else {
        filteredLectures = allLectures.where((course) {
          final matchesTitle =
              course.courseTitle.toLowerCase().contains(query.toLowerCase());
          return matchesTitle &&
              (selectedHorizontalCategories.isEmpty ||
                  selectedHorizontalCategories.contains(course.categoryName) ||
                  selectedHorizontalCategories
                      .contains(course.subcategoryName));
        }).toList();
      }
    });
  }

  void showLectureDetails(Course course) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          child: Container(
            width: 1000,
            height: 800,
            padding: EdgeInsets.all(16.0),
            child: SingleChildScrollView(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Image.network(
                        course.img ?? '',
                        fit: BoxFit.cover,
                        height: 400,
                        width: 400,
                      ),
                      SizedBox(width: 16.0),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Text(
                              course.courseTitle,
                              maxLines: 2,
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16.0,
                              ),
                            ),
                            SizedBox(height: 8.0),
                            Text(
                              course.platformName,
                              style: TextStyle(
                                  fontSize: 16.0, color: Colors.grey[600]),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 8.0),
                            Text(
                              course.subcategoryName,
                              style: TextStyle(
                                  fontSize: 16.0, color: Colors.grey[600]),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 8.0),
                            Text(
                              "${course.disPrice ?? course.regPrice ?? '월 27,147'} 원",
                              style: TextStyle(
                                  fontSize: 20.0, fontWeight: FontWeight.bold),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 8.0),
                            Text(
                              course.categoryName,
                              style: TextStyle(fontSize: 16.0),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 8.0),
                            Wrap(
                              alignment: WrapAlignment.center,
                              spacing: 6.0,
                              runSpacing: -4.0,
                              children: course.tags.map<Widget>((tag) {
                                return Chip(
                                  label: Text(tag),
                                  padding: EdgeInsets.symmetric(
                                      vertical: 2.0, horizontal: 8.0),
                                  labelStyle: TextStyle(fontSize: 10.0),
                                  backgroundColor: Colors.grey[100],
                                );
                              }).toList(),
                            ),
                            SizedBox(height: 16.0),
                            ElevatedButton(
                              onPressed: () {
                                Navigator.of(context).pop();
                                UrlLauncherService.launchURL(course.url);
                              },
                              child: Text('강의 사이트로 이동'),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 16.0),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Text(
                        '상세 정보',
                        style: TextStyle(
                            fontSize: 20.0, fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 8.0),
                      Text(
                        course.summary,
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 16.0),
                      Text(
                        '리뷰',
                        style: TextStyle(
                            fontSize: 20.0, fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 8.0),
                      ...course.reviewSummaries
                          .map((review) =>
                              Text(review, textAlign: TextAlign.center))
                          .toList(),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: PreferredSize(
        preferredSize: Size.fromHeight(330.0),
        child: AppBar(
          flexibleSpace: Padding(
            padding: const EdgeInsets.only(top: 40.0),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(left: 16.0),
                      child: Image.asset(
                        'assets/icons/logo.png',
                        height: 15.0,
                      ),
                    ),
                    SizedBox(width: 15.0),
                    Text(
                      '5기 Data Engineering',
                      style: TextStyle(
                          fontSize: 12.0, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                SizedBox(height: 10.0),
                Column(
                  children: [
                    Text(
                      '어떤 강의를 찾고 있나요?',
                      style: TextStyle(fontSize: 40.0),
                    ),
                    SizedBox(height: 20.0),
                    Container(
                      width: 600,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: TextField(
                          decoration: InputDecoration(
                            hintText: '검색어를 입력하세요.',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(25.0),
                            ),
                            filled: true,
                            fillColor: Colors.white,
                          ),
                          onChanged: (query) {
                            searchLectures(query);
                          },
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 30.0),
                Container(
                  height: 90.0,
                  alignment: Alignment.center,
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        HorizontalCategoryButton(
                          category: '프론트엔드',
                          isSelected:
                              selectedHorizontalCategories.contains('프론트엔드'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/web.png',
                        ),
                        HorizontalCategoryButton(
                          category: '백엔드',
                          isSelected:
                              selectedHorizontalCategories.contains('백엔드'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/backend.png',
                        ),
                        HorizontalCategoryButton(
                          category: '모바일 앱',
                          isSelected:
                              selectedHorizontalCategories.contains('모바일 앱'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/app.png',
                        ),
                        HorizontalCategoryButton(
                          category: '데브옵스 · 인프라',
                          isSelected: selectedHorizontalCategories
                              .contains('데브옵스 · 인프라'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/infra.png',
                        ),
                        HorizontalCategoryButton(
                          category: '데이터 사이언스',
                          isSelected:
                              selectedHorizontalCategories.contains('데이터 사이언스'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/datascience.png',
                        ),
                        HorizontalCategoryButton(
                          category: '인공지능',
                          isSelected:
                              selectedHorizontalCategories.contains('인공지능'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/ai.png',
                        ),
                        HorizontalCategoryButton(
                          category: '컴퓨터 사이언스',
                          isSelected:
                              selectedHorizontalCategories.contains('컴퓨터 사이언스'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/comscience.png',
                        ),
                        HorizontalCategoryButton(
                          category: '게임 개발',
                          isSelected:
                              selectedHorizontalCategories.contains('게임 개발'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/game.png',
                        ),
                        HorizontalCategoryButton(
                          category: '디자인',
                          isSelected:
                              selectedHorizontalCategories.contains('디자인'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/design.png',
                        ),
                        HorizontalCategoryButton(
                          category: '기타',
                          isSelected:
                              selectedHorizontalCategories.contains('기타'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/etc.png',
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          centerTitle: true,
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(40.0),
        child: CourseList(courses: filteredLectures), // 필터링된 강의 리스트 표시
      ),
    );
  }
}
