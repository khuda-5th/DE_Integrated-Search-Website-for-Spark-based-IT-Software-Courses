class Subcategory {
  final int subcategoryId;
  final String subcategoryName;
  final int categoryId;

  Subcategory({
    required this.subcategoryId,
    required this.subcategoryName,
    required this.categoryId,
  });

  factory Subcategory.fromJson(Map<String, dynamic> json) {
    return Subcategory(
      subcategoryId: json['subcategory_id'],
      subcategoryName: json['subcategory_name'],
      categoryId: json['category_id'],
    );
  }
}