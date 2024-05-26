import 'package:flutter/material.dart';
import '../models/course_model.dart';
import '../services/api_service.dart';
import 'course_item.dart';

class CourseList extends StatelessWidget {
  final ApiService apiService = ApiService();
  final List<Course> courses;
  CourseList({required this.courses});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Course>>(
      future: apiService.fetchCourses(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (snapshot.hasData) {
          final courses = snapshot.data ?? [];
          return Padding(
            padding: const EdgeInsets.all(8.0),
            child: GridView.builder(
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 4, // 열의 개수를 조정할 수 있습니다.
                crossAxisSpacing: 10.0,
                mainAxisSpacing: 10.0,
                childAspectRatio: 5/4,
              ),
              itemCount: courses.length,
              itemBuilder: (context, index) {
                final course = courses[index];
                return CourseItem(course: course); // course 하나만 나오는
              },
            ),
          );
        } else {
          return Center(child: Text('No data available'));
        }
      },
    );
  }
}