import 'package:flutter/material.dart';

class TagSearchBar extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSearch;

  const TagSearchBar({
    Key? key,
    required this.controller,
    required this.onSearch,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Column(
        children: [
          TextField(
            controller: controller,
            decoration: const InputDecoration(hintText: 'Enter your favorite talk'),
          ),
          ElevatedButton(
            child: const Text('Search by tag'),
            onPressed: onSearch,
          ),
        ],
      ),
    );
  }
}
