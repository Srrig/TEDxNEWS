import 'package:flutter/material.dart';
import 'api_service.dart'; // Importa il servizio API
import 'models/watch_next.dart'; // Importa il modello WatchNext

class WatchNextDetailPage extends StatefulWidget {
  final String videoId;

  const WatchNextDetailPage({Key? key, required this.videoId}) : super(key: key);

  @override
  _WatchNextDetailPageState createState() => _WatchNextDetailPageState();
}

class _WatchNextDetailPageState extends State<WatchNextDetailPage> {
  Future<WatchNext>? _videoFuture;

  @override
  void initState() {
    super.initState();
    _videoFuture = fetchVideoById(widget.videoId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Video Details"),
      ),
      body: FutureBuilder<WatchNext>(
        future: _videoFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (snapshot.hasData) {
            final video = snapshot.data!;
            final mainVideo = video.watchNext.isNotEmpty ? video.watchNext[0] : null;

            return SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  // Immagine del video principale, se disponibile
                  if (mainVideo != null && mainVideo.imageUrl != null)
                    Image.network(mainVideo.imageUrl!),
                  const SizedBox(height: 16.0),

                  // Titolo
                  Text(
                    video.title,
                    style: TextStyle(
                      fontSize: 25,
                      fontWeight: FontWeight.bold,
                      color: const Color.fromARGB(255, 96, 25, 25),
                    ),
                  ),
                  const SizedBox(height: 8.0),

                  // Descrizione
                  Text(
                    'Dettagli:',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    video.description,
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.black,
                    ),
                  ),
                  const SizedBox(height: 8.0),

                  // URL del video
                  if (mainVideo != null && mainVideo.url.isNotEmpty)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'URL:',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        Text(
                          mainVideo.url,
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: const Color.fromARGB(255, 19, 88, 144),
                          ),
                        ),
                      ],
                    ),
                ],
              ),
            );
          } else {
            return const Center(child: Text('No data found.'));
          }
        },
      ),
    );
  }
}

