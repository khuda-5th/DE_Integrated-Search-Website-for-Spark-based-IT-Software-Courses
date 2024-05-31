import 'package:flutter/material.dart';
import 'category_button.dart';

class CategorySlide extends StatelessWidget {
  final List<String> selectedCategories;
  final Function(String) onCategorySelected;

  CategorySlide(
      {required this.selectedCategories, required this.onCategorySelected});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 200,
      color: Colors.white, // 카테고리 슬라이드 배경을 흰색으로 설정
      child: ListView(
        children: [
          CategoryButton(
            category: '추천순',
            isSelected: selectedCategories.contains('추천순'),
            onCategorySelected: onCategorySelected,
          ),
          CategoryButton(
            category: '낮은 가격순',
            isSelected: selectedCategories.contains('낮은 가격순'),
            onCategorySelected: onCategorySelected,
          ),
          CategoryButton(
            category: '높은 가격순',
            isSelected: selectedCategories.contains('높은 가격순'),
            onCategorySelected: onCategorySelected,
          ),
          // 추가 카테고리들
        ],
      ),
    );
  }
}
