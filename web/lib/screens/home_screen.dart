import 'package:flutter/material.dart';
import '../widgets/category_slide.dart';
import '../widgets/horizontal_category_button.dart';
import '../services/url_launcher_service.dart';
import '../models/lecture.dart';
import '../models/subcategory.dart';
import '../widgets/course_item.dart';
import '../widgets/course_list.dart';


class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Lecture> allLectures = []; // 예시로 빈 리스트 설정
  List<Lecture> filteredLectures = [];
  List<Subcategory> subcategories = []; // 예시로 빈 리스트 설정
  List<String> selectedCategories = [];
  List<String> selectedHorizontalCategories = [];

  @override
  void initState() {
    super.initState();
    loadData(); // 초기 데이터 설정 함수 호출
  }

  // 데이터 초기화 함수
  void loadData() {
    // 여기에서 초기 데이터를 설정하세요.
    setState(() {
      allLectures = []; // 예시로 빈 리스트 설정
      subcategories = []; // 예시로 빈 리스트 설정
      filteredLectures = allLectures;
    });
  }

  void toggleCategory(String category) {
    setState(() {
      selectedCategories = [category];
      filterLectures();
    });
  }

  void toggleHorizontalCategory(String horizontalCategory) {
    setState(() {
      if (selectedHorizontalCategories.contains(horizontalCategory)) {
        selectedHorizontalCategories.remove(horizontalCategory);
      } else {
        selectedHorizontalCategories.add(horizontalCategory);
      }
      filterLectures();
    });
  }

  void filterLectures() {
    List<String> subcategoryNames = selectedHorizontalCategories.expand((category) {
      return getSubcategoriesForCategory(category);
    }).toList();

    List<Lecture> lecturesToFilter = List.from(allLectures);

    if (subcategoryNames.isNotEmpty) {
      lecturesToFilter = lecturesToFilter.where((lecture) {
        return subcategoryNames.contains(lecture.subcategoryName);
      }).toList();
    }

    if (selectedCategories.contains('낮은 가격순')) {
      lecturesToFilter.sort((a, b) => a.disPrice.compareTo(b.disPrice));
    } else if (selectedCategories.contains('높은 가격순')) {
      lecturesToFilter.sort((a, b) => b.disPrice.compareTo(a.disPrice));
    }

    setState(() {
      filteredLectures = lecturesToFilter;
    });
  }

  List<String> getSubcategoriesForCategory(String category) {
    switch (category) {
      case '프론트엔드':
        return ['프론트엔드', '풀스택'];
      case '백엔드':
        return ['데이터베이스', '백엔드', '풀스택'];
      case '데브옵스 · 인프라':
        return ['업무 자동화'];
      case '데이터 사이언스':
        return ['데이터 분석'];
      case '인공지능':
        return ['인공지능'];
      case '컴퓨터 사이언스':
        return ['Python', 'JavaScript', '프로그래밍 기초', '알고리즘·자료구조', '객체 지향 프로그래밍'];
      case '디자인':
        return ['디자인'];
      case '기타':
        return ['개발 도구', 'IT 교양'];
      default:
        return [];
    }
  }

  void searchLectures(String query) {
    setState(() {
      if (query.isEmpty) {
        filterLectures();
      } else {
        filteredLectures = allLectures.where((lecture) {
          final matchesTitle = lecture.courseTitle.toLowerCase().contains(query.toLowerCase());
          return matchesTitle && (selectedHorizontalCategories.isEmpty ||
              getSubcategoriesForCategory(lecture.subcategoryName).isNotEmpty);
        }).toList();
      }
    });
  }

  void showLectureDetails(Lecture lecture) {
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
                        lecture.img,
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
                              lecture.courseTitle,
                              style: TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 8.0),
                            Text(
                              lecture.platformName,
                              style: TextStyle(fontSize: 16.0, color: Colors.grey[600]),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 8.0),
                            Text(
                              '\$${lecture.disPrice}',
                              style: TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 8.0),
                            Text(
                              lecture.categoryName,
                              style: TextStyle(fontSize: 16.0),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 8.0),
                            Wrap(
                              alignment: WrapAlignment.center,
                              spacing: 6.0,
                              runSpacing: -4.0,
                              children: lecture.tags.map<Widget>((tag) {
                                return Chip(
                                  label: Text(tag),
                                  padding: EdgeInsets.symmetric(vertical: 2.0, horizontal: 8.0),
                                  labelStyle: TextStyle(fontSize: 10.0),
                                  backgroundColor: Colors.grey[100],
                                );
                              }).toList(),
                            ),
                            SizedBox(height: 16.0),
                            ElevatedButton(
                              onPressed: () {
                                Navigator.of(context).pop();
                                UrlLauncherService.launchURL(lecture.url);
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
                        style: TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 8.0),
                      Text(
                        lecture.summary,
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 16.0),
                      Text(
                        '리뷰',
                        style: TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 8.0),
                      Text('리뷰 1', textAlign: TextAlign.center),
                      Text('리뷰 2', textAlign: TextAlign.center),
                      Text('리뷰 3', textAlign: TextAlign.center),
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
                      style: TextStyle(fontSize: 12.0, fontWeight: FontWeight.bold),
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
                            hintText: '   검색어를 입력하세요.',
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
                          isSelected: selectedHorizontalCategories.contains('프론트엔드'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/web.png',
                        ),
                        HorizontalCategoryButton(
                          category: '백엔드',
                          isSelected: selectedHorizontalCategories.contains('백엔드'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/backend.png',
                        ),
                        HorizontalCategoryButton(
                          category: '모바일 앱',
                          isSelected: selectedHorizontalCategories.contains('모바일 앱'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/app.png',
                        ),
                        HorizontalCategoryButton(
                          category: '데브옵스 · 인프라',
                          isSelected: selectedHorizontalCategories.contains('데브옵스 · 인프라'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/infra.png',
                        ),
                        HorizontalCategoryButton(
                          category: '데이터 사이언스',
                          isSelected: selectedHorizontalCategories.contains('데이터 사이언스'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/datascience.png',
                        ),
                        HorizontalCategoryButton(
                          category: '인공지능',
                          isSelected: selectedHorizontalCategories.contains('인공지능'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/ai.png',
                        ),
                        HorizontalCategoryButton(
                          category: '컴퓨터 사이언스',
                          isSelected: selectedHorizontalCategories.contains('컴퓨터 사이언스'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/comscience.png',
                        ),
                        HorizontalCategoryButton(
                          category: '게임 개발',
                          isSelected: selectedHorizontalCategories.contains('게임 개발'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/game.png',
                        ),
                        HorizontalCategoryButton(
                          category: '디자인',
                          isSelected: selectedHorizontalCategories.contains('디자인'),
                          onCategorySelected: toggleHorizontalCategory,
                          imagePath: 'assets/icons/design.png',
                        ),
                        HorizontalCategoryButton(
                          category: '기타',
                          isSelected: selectedHorizontalCategories.contains('기타'),
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
        child: Row(
          children: [
            CategorySlide(
              selectedCategories: selectedCategories,
              onCategorySelected: toggleCategory,
            ),
            SizedBox(width: 30.0),
            Expanded(
              child: CourseList(),
            ),
          ],
        ),
      ),
    );
  }
}
