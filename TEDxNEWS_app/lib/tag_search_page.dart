import 'package:flutter/material.dart';
import 'talk_repository.dart';
import 'models/talk.dart';
import 'talk_detail_page.dart'; // Importa la pagina dei dettagli

class TagSearchPage extends StatefulWidget {
  final String initialTag;

  const TagSearchPage({Key? key, this.initialTag = ''}) : super(key: key);

  @override
  _TagSearchPageState createState() => _TagSearchPageState();
}

class _TagSearchPageState extends State<TagSearchPage> {
  final TextEditingController _controller = TextEditingController();
  late Future<List<Talk>> _talks;
  int page = 1;
  bool init = true;

  @override
  void initState() {
    super.initState();
    _controller.text = widget.initialTag;
    _talks = initEmptyList();
    if (_controller.text.isNotEmpty) {
      _getTalksByTag();
    }
  }

  void _getTalksByTag() async {
    setState(() {
      init = false;
      _talks = getTalksByTag(_controller.text, page);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          init ? 'Search Talks' : "#${_controller.text}",
          style: const TextStyle(
            fontFamily: 'Roboto',
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.black,
          ),
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                TextField(
                  controller: _controller,
                  decoration: InputDecoration(
                    hintText: 'Enter your favorite talk',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                    ),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.search),
                      onPressed: () {
                        page = 1;
                        _getTalksByTag();
                      },
                    ),
                  ),
                  onSubmitted: (value) {
                    page = 1;
                    _getTalksByTag();
                  },
                ),
                const SizedBox(height: 16.0),
              ],
            ),
          ),
          Expanded(
            child: (init)
                ? Center(child: Text('Search for talks by tag to see results.'))
                : FutureBuilder<List<Talk>>(
                    future: _talks,
                    builder: (context, snapshot) {
                      if (snapshot.hasData) {
                        return ListView.builder(
                          itemCount: snapshot.data!.length,
                          itemBuilder: (context, index) {
                            final talk = snapshot.data![index];
                            return Card(
                              margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
                              child: ListTile(
                                contentPadding: const EdgeInsets.all(16.0),
                                title: Text(talk.title),
                                subtitle: Text('by ${talk.mainSpeaker}'),
                                onTap: () {
                                  Navigator.of(context).push(
                                    MaterialPageRoute(
                                      builder: (context) => TalkDetailPage(talk: talk),
                                    ),
                                  );
                                },
                              ),
                            );
                          },
                        );
                      } else if (snapshot.hasError) {
                        return Center(child: Text("${snapshot.error}"));
                      }

                      return const Center(child: CircularProgressIndicator());
                    },
                  ),
          ),
        ],
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      floatingActionButton: FloatingActionButton(
        child: const Icon(Icons.arrow_drop_down),
        onPressed: () {
          if (!init && _controller.text.isNotEmpty) {
            page = page + 1;
            _getTalksByTag();
          }
        },
      ),
      bottomNavigationBar: BottomAppBar(
        child: Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: <Widget>[
            IconButton(
              icon: const Icon(Icons.home),
              onPressed: () {
                Navigator.of(context).pop(); // Torna alla pagina precedente
              },
            ),
          ],
        ),
      ),
    );
  }
}

