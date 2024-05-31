import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:lecture_web/models/search_course_model.dart';
import '../models/platform_model.dart';
import '../models/category_model.dart';
import '../models/course_model.dart';
import '../utils/constants.dart';

class ApiService {
  Future<List<Platform>> fetchPlatforms() async {
    try {
      final response = await http.get(Uri.parse('$API_BASE_URL/platforms'));

      if (response.statusCode == 200) {
        List jsonResponse = json.decode(utf8.decode(response.bodyBytes));
        return jsonResponse
            .map((platform) => Platform.fromJson(platform))
            .toList();
      } else {
        throw Exception('Failed to load platforms');
      }
    } catch (e) {
      throw Exception('Failed to load platforms');
    }
  }

  Future<List<Category>> fetchCategories() async {
    try {
      final response = await http.get(Uri.parse('$API_BASE_URL/categories'));

      if (response.statusCode == 200) {
        List jsonResponse = json.decode(utf8.decode(response.bodyBytes));
        return jsonResponse
            .map((category) => Category.fromJson(category))
            .toList();
      } else {
        throw Exception('Failed to load categories');
      }
    } catch (e) {
      throw Exception('Failed to load categories');
    }
  }

  Future<List<Course>> fetchCourses(int page, int pageSize) async {
    try {
      final response = await http.get(
        Uri.parse('$API_BASE_URL/courses?page=$page&page_size=$pageSize'),
      );

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(utf8.decode(response.bodyBytes));
        final List coursesJson = jsonResponse['courses'];
        return coursesJson.map((course) => Course.fromJson(course)).toList();
      } else {
        throw Exception('Failed to load courses');
      }
    } catch (e) {
      throw Exception('Failed to load courses: $e');
    }
  }

  Future<List<SearchCourse>> searchCourses(String query) async {
    try {
      final response =
          await http.get(Uri.parse('$API_BASE_URL/search?keyword=$query'));
      if (response.statusCode == 200) {
        final List<dynamic> jsonResponse =
            json.decode(utf8.decode(response.bodyBytes));
        return jsonResponse
            .map((course) => SearchCourse.fromJson(course))
            .toList();
      } else {
        throw Exception('Failed to load courses');
      }
    } catch (e) {
      throw Exception('Failed to load courses: $e');
    }
  }
}
