import 'dart:convert';
import 'package:http/http.dart' as http;
import 'models/watch_next.dart'; // Importa il modello WatchNext

Future<WatchNext> fetchVideoById(String id) async {
  final url = Uri.parse('https://84io1o9jfk.execute-api.us-east-1.amazonaws.com/default/Get_TalkId_by_Idx');

  final response = await http.post(
    url,
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{
      'idx': id,
    }),
  );

  print('Request URL: $url');
  print('Request body: ${jsonEncode(<String, String>{'idx': id})}');
  print('Response status: ${response.statusCode}');
  print('Response body: ${response.body}');

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    if (data.isNotEmpty) {
      return WatchNext.fromJson(data);
    } else {
      throw Exception('Empty response data');
    }
  } else {
    throw Exception('Failed to load video');
  }
}


