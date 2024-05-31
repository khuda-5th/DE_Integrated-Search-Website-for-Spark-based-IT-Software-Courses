import 'package:flutter/material.dart';
import 'package:lecture_web/models/base_course_model.dart';
import 'package:lecture_web/models/subsection_model.dart';
import '../services/url_launcher_service.dart';

class LectureDetailsScreen extends StatelessWidget {
  final BaseCourse course;

  const LectureDetailsScreen({required this.course});

  @override
  Widget build(BuildContext context) {
    double screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      appBar: AppBar(
        title: Text(course.courseTitle),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              const SizedBox(height: 50),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(width: 200.0),
                  SizedBox(
                    width: 400,
                    height: 200,
                    child: Image.network(
                      course.img ?? '',
                      fit: BoxFit.contain,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          course.courseTitle,
                          style: const TextStyle(
                              fontSize: 30.0, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 15.0),
                        Text(
                          course.platformName,
                          style: TextStyle(
                              fontSize: 20.0, color: Colors.grey[600]),
                        ),
                        const SizedBox(height: 8.0),
                        Text(
                          course.subcategoryName,
                          style: TextStyle(
                              fontSize: 20.0, color: Colors.grey[600]),
                        ),
                        const SizedBox(height: 30.0),
                        Text(
                          "${course.disPrice ?? course.regPrice ?? '월 27,147'} 원",
                          style: const TextStyle(
                              fontSize: 20.0, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 20.0),
                        Wrap(
                          alignment: WrapAlignment.start,
                          spacing: 6.0,
                          runSpacing: -4.0,
                          children: course.tags.map<Widget>((tag) {
                            return Chip(
                              label: Text(tag),
                              padding: const EdgeInsets.symmetric(
                                  vertical: 2.0, horizontal: 8.0),
                              labelStyle: const TextStyle(fontSize: 10.0),
                              backgroundColor: Colors.grey[100],
                            );
                          }).toList(),
                        ),
                        const SizedBox(height: 16.0),
                        ElevatedButton(
                          onPressed: () {
                            UrlLauncherService.launchURL(course.url);
                          },
                          child: const Text(
                            '강의 사이트로 이동',
                            style: TextStyle(
                                fontSize: 20.0, fontWeight: FontWeight.bold),
                          ),
                          style: ElevatedButton.styleFrom(
                            minimumSize: const Size(330, 60),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 60.0),
              Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const Text(
                    '강의 요약',
                    style:
                        TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 10.0),
                  Text(
                    course.summary,
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
              const SizedBox(height: 60.0),
              Padding(
                padding: EdgeInsets.only(left: screenWidth * 0.2), // 왼쪽 마진 설정
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (course.reviewSummaries.isNotEmpty) ...[
                      const Text(
                        '리뷰',
                        style: TextStyle(
                            fontSize: 20.0, fontWeight: FontWeight.bold),
                        textAlign: TextAlign.start,
                      ),
                      const SizedBox(height: 8.0),
                      ...course.reviewSummaries.map(
                          (review) => Text(review, textAlign: TextAlign.start)),
                      const SizedBox(height: 60.0),
                    ],
                    const Text(
                      '강의 섹션',
                      style: TextStyle(
                          fontSize: 20.0, fontWeight: FontWeight.bold),
                      textAlign: TextAlign.start,
                    ),
                    ...course.sections.asMap().entries.map((entry) {
                      int sectionIndex = entry.key;
                      Section section = entry.value;
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Part ${sectionIndex + 1}. ${section.sectionName}',
                              style: const TextStyle(
                                  fontSize: 18.0, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 8.0),
                            ...section.subsections
                                .asMap()
                                .entries
                                .map((subEntry) {
                              int subIndex = subEntry.key;
                              SubSection subsection = subEntry.value;
                              return Padding(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 4.0),
                                child: Text(
                                  '${subIndex + 1}) ${subsection.subsectionName}',
                                  style: const TextStyle(fontSize: 16.0),
                                ),
                              );
                            }),
                          ],
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
