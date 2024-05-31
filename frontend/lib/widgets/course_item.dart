import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:lecture_web/models/base_course_model.dart';
import '../screens/lecture_details_screen.dart';

class CourseItem extends StatelessWidget {
  final BaseCourse course;

  CourseItem({required this.course});

  @override
  Widget build(BuildContext context) {
    const defaultImageUrl = '../assets/icons/null.png';
    final imageUrl = (course.img != null && course.img!.isNotEmpty)
        ? '${course.img}?w=200&h=100'
        : defaultImageUrl;

    return LayoutBuilder(
      builder: (context, constraints) {
        final imageHeight = constraints.maxHeight * 0.40;
        final imageWidth = constraints.maxWidth * 0.95;
        final remainingHeight = constraints.maxHeight - imageHeight;

        return Card(
          margin: const EdgeInsets.all(8.0),
          child: InkWell(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => LectureDetailsScreen(course: course),
                ),
              );
            },
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CachedNetworkImage(
                  imageUrl: imageUrl,
                  placeholder: (context, url) => const Center(
                    child: CircularProgressIndicator(),
                  ),
                  errorWidget: (context, url, error) => const Icon(Icons.error),
                  fit: BoxFit.cover,
                  height: imageHeight,
                  width: imageWidth,
                ),
                SizedBox(
                  height: remainingHeight * 0.05,
                ), // Padding between image and text
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        course.courseTitle,
                        maxLines: 2,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16.0,
                        ),
                      ),
                      SizedBox(height: remainingHeight * 0.05),
                      Text(
                        "${course.disPrice ?? course.regPrice ?? '월 27,147'} 원",
                      ),
                      SizedBox(height: remainingHeight * 0.05),
                      Text(
                        course.platformName,
                        style: TextStyle(
                          fontSize: 12.0,
                          color: Colors.grey[600],
                        ),
                      ),
                      SizedBox(height: remainingHeight * 0.1),
                      SizedBox(
                        height: remainingHeight * 0.2,
                        child: ListView(
                          scrollDirection: Axis.horizontal,
                          children: course.tags.map<Widget>((tag) {
                            return Chip(
                              label: Text(tag),
                              padding: const EdgeInsets.symmetric(
                                vertical: 2.0,
                                horizontal: 8.0,
                              ),
                              labelStyle: const TextStyle(fontSize: 10.0),
                              backgroundColor: Colors.grey[100],
                            );
                          }).toList(),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
