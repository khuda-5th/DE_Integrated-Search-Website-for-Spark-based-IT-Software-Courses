class Platform {
  final int id;
  final String name;

  Platform({required this.id, required this.name});

  factory Platform.fromJson(Map<String, dynamic> json) {
    return Platform(
      id: json['platform_id'],
      name: json['platform_name'],
    );
  }
}
