import 'package:flutter/material.dart';
import 'api_service.dart'; // Importa il servizio API
import 'models/watch_next.dart'; // Importa il modello WatchNext
import 'introduction_page.dart';
import 'tag_search_page.dart'; // Importa la pagina di ricerca per tag
import 'watch_next_detail_page.dart'; // Importa la pagina dei dettagli del video

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        primarySwatch: Colors.red,
        scaffoldBackgroundColor: Colors.red,
        appBarTheme: const AppBarTheme(
          color: Colors.white,
          titleTextStyle: TextStyle(
            fontFamily: 'Roboto',
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
          centerTitle: true,
        ),
      ),
      home: const IntroductionPage(), // Imposta la pagina di introduzione come home
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, this.title = ''});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Future<WatchNext>? _videoFuture;

  @override
  void initState() {
    super.initState();
    _videoFuture = fetchVideoById('297805'); 
  }

  void _showHelpDialog(BuildContext context) {
    TextEditingController _textController = TextEditingController();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Hai bisogno di aiuto?'),
          content: TextField(
            controller: _textController,
            decoration: const InputDecoration(
              hintText: 'Inserisci la tua domanda qui',
            ),
          ),
          actions: <Widget>[
            TextButton(
              child: const Text('Invia'),
              onPressed: () {
                // Qui puoi gestire l'invio della domanda
                Navigator.of(context).pop();
              },
            ),
            TextButton(
              child: const Text('Chiudi'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Expanded(
              child: FittedBox(
                fit: BoxFit.contain,
                child: Image.asset(
                  'assets/images/logo.png',
                ),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline, color: Colors.red),
            onPressed: () {
              _showHelpDialog(context);
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          Positioned(
            top: 16.0,
            right: 16.0,
            child: ElevatedButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const TagSearchPage(),
                  ),
                );
              },
              child: const Text('Search by TAG'),
            ),
          ),
          Positioned(
            top: 80.0,
            left: 16.0,
            right: 16.0,
            bottom: 16.0,
            child: FutureBuilder<WatchNext>(
              future: _videoFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                } else if (snapshot.hasError) {
                  return Center(child: Text('Error: ${snapshot.error}'));
                } else if (snapshot.hasData) {
                  final watchNext = snapshot.data!;
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      const Padding(
                        padding: EdgeInsets.all(8.0),
                        child: Text(
                          'Consigliati',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      Expanded(
                        child: ListView.builder(
                          itemCount: watchNext.watchNext.length,
                          itemBuilder: (context, index) {
                            final relatedVideo = watchNext.watchNext[index];
                            return ListTile(
                              leading: relatedVideo.imageUrl != null
                                  ? Stack(
                                      children: [
                                        Image.network(relatedVideo.imageUrl!),
                                        Positioned.fill(
                                          child: Align(
                                            alignment: Alignment.center,
                                            child: Icon(
                                              Icons.play_circle_fill,
                                              color: Colors.white,
                                              size: 40,
                                            ),
                                          ),
                                        ),
                                      ],
                                    )
                                  : null, // Mostra l'immagine se disponibile
                              title: Text(relatedVideo.title),
                              onTap: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute(
                                    builder: (context) => WatchNextDetailPage(videoId: relatedVideo.id),
                                  ),
                                );
                              },
                            );
                          },
                        ),
                      ),
                    ],
                  );
                } else {
                  return const Center(child: Text('No data found.'));
                }
              },
            ),
          ),
        ],
      ),
    );
  }
}

