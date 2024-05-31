import 'package:flutter/material.dart';
import 'package:lecture_web/models/base_course_model.dart';
import '../services/api_service.dart';
import '../utils/filter_lectures.dart'; // 올바른 filterLectures 함수 import
import '../widgets/category_slide.dart';
import '../widgets/course_list.dart'; // 중복되지 않도록 필요한 곳에서만 import
import '../widgets/horizontal_category_button.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<BaseCourse> allLectures = [];
  List<BaseCourse> filteredLectures = [];
  List<String> selectedCategories = [];
  List<String> selectedHorizontalCategories = [];
  final TextEditingController _searchController = TextEditingController();
  final ApiService apiService = ApiService();
  int _currentPage = 1;
  final int _pageSize = 50;
  bool _isLoading = false;
  bool _hasMoreCourses = true;

  @override
  void initState() {
    super.initState();
    loadData();
  }

  Future<void> loadData() async {
    setState(() {
      _isLoading = true;
    });
    try {
      List<BaseCourse> courses =
          await apiService.fetchCourses(_currentPage, _pageSize);
      setState(() {
        allLectures.addAll(courses);
        filteredLectures = filterLectures(
          allLectures: allLectures,
          selectedHorizontalCategories: selectedHorizontalCategories,
          selectedCategories: selectedCategories,
        );
        _currentPage++;
        _isLoading = false;
        if (courses.length < _pageSize) {
          _hasMoreCourses = false;
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _hasMoreCourses = false;
      });
      print('Error loading data: $e');
    }
  }

  void toggleCategory(String category) {
    setState(() {
      selectedCategories = [category];
      applyFilters();
    });
  }

  void toggleHorizontalCategory(String horizontalCategory) {
    setState(() {
      if (selectedHorizontalCategories.contains(horizontalCategory)) {
        selectedHorizontalCategories.remove(horizontalCategory);
      } else {
        selectedHorizontalCategories.add(horizontalCategory);
      }
      applyFilters();
    });
  }

  void applyFilters() {
    setState(() {
      filteredLectures = filterLectures(
        allLectures: allLectures,
        selectedHorizontalCategories: selectedHorizontalCategories,
        selectedCategories: selectedCategories,
      );
    });
  }

  void searchLectures(String query) async {
    setState(() {
      _isLoading = true;
    });
    try {
      List<BaseCourse> searchResults = await apiService.searchCourses(query);
      setState(() {
        filteredLectures = searchResults;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        filteredLectures = [];
        _isLoading = false;
      });
      print('Error searching lectures: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    double screenHeight = MediaQuery.of(context).size.height;
    double screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: PreferredSize(
        preferredSize: Size.fromHeight(screenHeight * 0.4),
        child: AppBar(
          flexibleSpace: Padding(
            padding: EdgeInsets.only(top: screenHeight * 0.03),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(left: 16.0),
                      child: Image.asset('assets/icons/logo.png', height: 15.0),
                    ),
                    const SizedBox(width: 15.0),
                    const Text(
                      '5기 Data Engineering',
                      style: TextStyle(
                          fontSize: 12.0, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 10.0),
                Column(
                  children: [
                    const Text(
                      '어떤 강의를 찾고 있나요?',
                      style: TextStyle(fontSize: 40.0),
                    ),
                    Padding(padding: EdgeInsets.all(screenHeight * 0.01)),
                    SizedBox(
                      width: screenWidth * 0.5,
                      child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0),
                          child: Row(
                            children: [
                              Expanded(
                                child: TextField(
                                  controller: _searchController,
                                  decoration: InputDecoration(
                                    hintText: '검색어를 입력하세요.',
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(25.0),
                                    ),
                                    filled: true,
                                    fillColor: Colors.white,
                                  ),
                                  onSubmitted: (query) {
                                    searchLectures(query);
                                  },
                                ),
                              ),
                              const SizedBox(width: 10),
                              ElevatedButton(
                                onPressed: () {
                                  searchLectures(_searchController.text);
                                },
                                child: const Text('검색'),
                              ),
                            ],
                          )),
                    ),
                  ],
                ),
                SizedBox(height: screenHeight * 0.04),
                Container(
                  height: screenHeight * 0.1,
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
        child: Row(
          children: [
            SizedBox(
              width: screenWidth * 0.15,
              child: CategorySlide(
                selectedCategories: selectedCategories,
                onCategorySelected: toggleCategory,
              ),
            ),
            const Padding(padding: EdgeInsets.all(10)),
            Expanded(
              child: filteredLectures.isEmpty
                  ? const Center(child: Text('검색 결과가 없습니다.'))
                  : CourseList(
                      courses: filteredLectures,
                      onEndReached: () {
                        if (_hasMoreCourses && !_isLoading) {
                          loadData();
                        }
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
