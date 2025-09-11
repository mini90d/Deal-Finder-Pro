class Deal {
  final String id;
  final String name;
  final String description;
  final double discountPercentage;
  final double? originalPrice;
  final double? discountedPrice;
  final String businessName;
  final String? imageUrl;
  final List<String> tags;
  final DealLocation location;

  Deal({
    required this.id,
    required this.name,
    required this.description,
    required this.discountPercentage,
    this.originalPrice,
    this.discountedPrice,
    required this.businessName,
    this.imageUrl,
    required this.tags,
    required this.location,
  });

  factory Deal.fromJson(Map<String, dynamic> json) {
    return Deal(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      discountPercentage: (json['discountPercentage'] as num).toDouble(),
      originalPrice: (json['originalPrice'] as num?)?.toDouble(),
      discountedPrice: (json['discountedPrice'] as num?)?.toDouble(),
      businessName: json['businessName'],
      imageUrl: json['imageUrl'],
      tags: List<String>.from(json['tags']),
      location: DealLocation.fromJson(json['location']),
    );
  }
}

class DealLocation {
  final String type;
  final List<double> coordinates;

  DealLocation({required this.type, required this.coordinates});

  factory DealLocation.fromJson(Map<String, dynamic> json) {
    return DealLocation(
      type: json['type'],
      coordinates: List<double>.from(json['coordinates'].map((c) => (c as num).toDouble())),
    );
  }

  double get longitude => coordinates[0];
  double get latitude => coordinates[1];
}
