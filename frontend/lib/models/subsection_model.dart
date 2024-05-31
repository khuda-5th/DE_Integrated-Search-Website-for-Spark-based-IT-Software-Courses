class SubSection {
  final int subsectionNum;
  final String subsectionName;

  SubSection({
    required this.subsectionNum,
    required this.subsectionName,
  });

  factory SubSection.fromJson(Map<String, dynamic> json) {
    return SubSection(
      subsectionNum: json['subsection_num'],
      subsectionName: json['subsection_name'],
    );
  }
}

class Section {
  final int sectionNum;
  final String sectionName;
  final List<SubSection> subsections;

  Section({
    required this.sectionNum,
    required this.sectionName,
    required this.subsections,
  });

  factory Section.fromJson(Map<String, dynamic> json) {
    return Section(
      sectionNum: json['section_num'],
      sectionName: json['section_name'],
      subsections: (json['subsections'] as List)
          .map((subsection) => SubSection.fromJson(subsection))
          .toList(),
    );
  }
}
