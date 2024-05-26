import 'dart:convert';
import 'package:http/http.dart' as http;
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

  Future<List<Course>> fetchCourses() async {
    try {
      final response = await http.get(Uri.parse('$API_BASE_URL/courses'));

      if (response.statusCode == 200) {
        List jsonResponse = json.decode(utf8.decode(response.bodyBytes));
        return jsonResponse.map((course) => Course.fromJson(course)).toList();
      } else {
        throw Exception('Failed to load courses');
        print("코스 없음");
      }
    } catch (e) {
      throw Exception('Failed to load courses');
      print(e);
    }
  }
}