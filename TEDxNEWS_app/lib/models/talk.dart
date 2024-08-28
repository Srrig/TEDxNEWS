class Talk {
  final String title;
  final String details;
  final String mainSpeaker;
  final String url;
  final String duration;
  final String publishedAt;

  Talk.fromJSON(Map<String, dynamic> jsonMap) :
    title = jsonMap['title'] ?? 'Untitled', // Valore predefinito se null
    details = jsonMap['description'] ?? 'No details available', // Valore predefinito se null
    mainSpeaker = (jsonMap['speakers'] ?? ""),
    url = (jsonMap['url'] ?? ""),
    duration = jsonMap['duration'] ?? "",
    publishedAt = jsonMap['publishedAt'] ?? "";
}
