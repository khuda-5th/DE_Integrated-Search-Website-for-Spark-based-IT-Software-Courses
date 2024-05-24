import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../models/course_model.dart';

class CourseItem extends StatelessWidget {
  final Course course;

  CourseItem({required this.course});

  @override
  Widget build(BuildContext context) {
    final defaultImageUrl = '../assets/icons/null.png';
    final imageUrl = (course.img != null && course.img!.isNotEmpty)
        ? '${course.img}?w=200&h=100'
        : defaultImageUrl;

    return Card(
      margin: const EdgeInsets.all(8.0),
      child: InkWell(
        onTap: () => {},
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
          CachedNetworkImage(
            imageUrl: imageUrl,
            placeholder: (context, url) => CircularProgressIndicator(),
            errorWidget: (context, url, error) => Icon(Icons.error),
            fit: BoxFit.cover,
            height: 100,
            width: double.infinity,
          ),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    course.courseTitle,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16.0,
                    ),
                  ),
                  SizedBox(height: 4.0),
                  Text('${course.disPrice}'),
                  SizedBox(height: 4.0),
                  Text(
                    course.platformName,
                    style: TextStyle(
                      fontSize: 12.0,
                      color: Colors.grey[600],
                    ),
                  ),
                  SizedBox(height: 8.0),
                  Wrap(
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
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
