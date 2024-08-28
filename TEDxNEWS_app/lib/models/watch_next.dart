import 'related_video.dart';

class WatchNext {
  final String id;
  final String title;
  final String description;
  final List<RelatedVideo> watchNext;

  WatchNext({
    required this.id,
    required this.title,
    required this.description,
    required this.watchNext,
  });

  factory WatchNext.fromJson(Map<String, dynamic> json) {
    return WatchNext(
      id: json['_id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      watchNext: (json['watch_next'] as List<dynamic>?)
              ?.map((video) => RelatedVideo.fromJson(video as Map<String, dynamic>))
              .toList() ??
          [], // Inizializza come lista vuota se null
    );
  }
}
