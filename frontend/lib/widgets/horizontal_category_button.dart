import 'package:flutter/material.dart';

class HorizontalCategoryButton extends StatelessWidget {
  final String category;
  final bool isSelected;
  final Function(String) onCategorySelected;
  final String imagePath;

  const HorizontalCategoryButton({
    super.key,
    required this.category,
    required this.isSelected,
    required this.onCategorySelected,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8.0),
      child: GestureDetector(
        onTap: () => onCategorySelected(category),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.asset(
              imagePath,
              height: 40.0,
              width: 120.0,
            ),
            const SizedBox(height: 4.0), // 아이콘과 텍스트 사이의 간격
            Text(
              category,
              style: TextStyle(color: isSelected ? Colors.blue : Colors.black),
            ),
          ],
        ),
      ),
    );
  }
}
