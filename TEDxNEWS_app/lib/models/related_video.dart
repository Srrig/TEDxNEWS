class RelatedVideo {
  final String id;
  final String title;
  final String url;
  final String? imageUrl; 

  RelatedVideo({
    required this.id,
    required this.title,
    required this.url,
    this.imageUrl, // Permetti valori nulli qui
  });

  factory RelatedVideo.fromJson(Map<String, dynamic> json) {
    return RelatedVideo(
      id: json['_id'] as String? ?? '', // Usa valori di default se è nullo
      title: json['title'] as String? ?? '',
      url: json['url'] as String? ?? '',
      imageUrl: json['image_url'] as String?, 
    );
  }
}
