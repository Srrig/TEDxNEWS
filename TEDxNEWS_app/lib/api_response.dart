// api_response.dart
import 'models/watch_next.dart';

class ApiResponse {
  final WatchNext video;

  ApiResponse({required this.video});

  factory ApiResponse.fromJson(Map<String, dynamic> json) {
    return ApiResponse(
      video: WatchNext.fromJson(json),
    );
  }
}
