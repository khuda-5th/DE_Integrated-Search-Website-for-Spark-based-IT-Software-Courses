import 'package:flutter/material.dart';
import 'package:lecture_web/models/base_course_model.dart';
import 'package:lecture_web/widgets/course_item.dart'; // 올바른 import 추가

class CourseList extends StatefulWidget {
  final List<BaseCourse> courses;
  final VoidCallback onEndReached;

  CourseList({required this.courses, required this.onEndReached});

  @override
  _CourseListState createState() => _CourseListState();
}

class _CourseListState extends State<CourseList> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels ==
        _scrollController.position.maxScrollExtent) {
      widget.onEndReached();
    }
  }

  @override
  Widget build(BuildContext context) {
    final double screenWidth = MediaQuery.of(context).size.width;
    final double screenHeight = MediaQuery.of(context).size.height;

    final bool isMobile = screenWidth < 600;
    final double itemWidth = isMobile ? screenWidth * 0.45 : screenWidth * 0.18;
    final double itemHeight = screenHeight * 0.45;

    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: GridView.builder(
        controller: _scrollController,
        gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
          maxCrossAxisExtent: itemWidth,
          crossAxisSpacing: 10.0,
          mainAxisSpacing: 10.0,
          childAspectRatio: itemWidth / itemHeight,
        ),
        itemCount: widget.courses.length,
        itemBuilder: (context, index) {
          final course = widget.courses[index];
          return CourseItem(course: course);
        },
      ),
    );
  }
}
