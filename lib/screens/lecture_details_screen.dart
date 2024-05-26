import 'package:flutter/material.dart';
import '../models/course_model.dart';
import '../services/url_launcher_service.dart';

class LectureDetailsScreen extends StatelessWidget {
  final Course course;

  LectureDetailsScreen({required this.course});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(course.courseTitle),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              SizedBox(height: 50),
              Row(
                children: [
                  SizedBox(width: 200.0),
                  Container(
                    width: 400,
                    height: 200,
                    child: Image.network(
                      course.img ?? '',
                      fit: BoxFit.contain,
                    ),
                  ),
                  SizedBox(width:10),
                  Expanded(
                    child: Column(
                      children: [
                        Text(
                          course.courseTitle,
                          style: TextStyle(
                              fontSize: 30.0, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 15.0),
                        Text(
                          course.platformName,
                          style: TextStyle(
                              fontSize: 20.0, color: Colors.grey[600]),
                        ),
                        SizedBox(height: 8.0),
                        Text(
                          course.subcategoryName,
                          style: TextStyle(
                              fontSize: 20.0, color: Colors.grey[600]),
                        ),
                        SizedBox(height: 30.0),
                        Text(
                          "${course.disPrice ?? course.regPrice ?? '월 27,147'} 원",
                          style: TextStyle(
                              fontSize: 20.0, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 20.0),
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
                            UrlLauncherService.launchURL(course.url);
                          },
                          child: Text(
                              '강의 사이트로 이동',
                            style: TextStyle(
                                fontSize: 20.0, fontWeight: FontWeight.bold),
                          ),
                          style: ElevatedButton.styleFrom(
                            minimumSize: Size(330, 60), // 버튼 크기 조정
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              SizedBox(height: 60.0),
              Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Text(
                    '상세 정보',
                    style:
                        TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 10.0),
                  Text(
                    course.summary,
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 60.0),
                  Text(
                    '리뷰',
                    style:
                        TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 8.0),
                  ...course.reviewSummaries
                      .map(
                          (review) => Text(review, textAlign: TextAlign.center))
                      .toList(),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
