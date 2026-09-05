/// Pack picker — choose an NER content pack + difficulty, then start Match It.
library;

import 'package:flutter/material.dart';

import '../data/local_content_packs.dart';
import '../models/shared_models.dart';
import '../services/api_service.dart';
import 'match_it_screen.dart';

class PackPickerScreen extends StatefulWidget {
  const PackPickerScreen({super.key});

  @override
  State<PackPickerScreen> createState() => _PackPickerScreenState();
}

class _PackPickerScreenState extends State<PackPickerScreen> {
  final ApiService _api = ApiService.instance;

  List<ContentPackSummary>? _packs;
  bool _loading = true;
  String? _error;
  int _difficulty = 1;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final packs = await _api.listContentPacks();
      if (!mounted) return;
      setState(() {
        _packs = packs;
        _loading = false;
      });
    } on Exception {
      if (!mounted) return;
      setState(() {
        _packs = LocalContentPacks.summaries;
        _loading = false;
      });
    }
  }

  void _start(ContentPackSummary pack) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => MatchItScreen(
          packId: pack.id,
          packName: pack.name,
          difficultyLevel: _difficulty,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Choose a Game', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(_error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 17)),
                      const SizedBox(height: 16),
                      ElevatedButton(onPressed: _load, child: const Text('Retry')),
                    ],
                  ),
                )
              : Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: SegmentedButton<int>(
                        segments: const [
                          ButtonSegment(value: 1, label: Text('Easy'), icon: Icon(Icons.sentiment_satisfied)),
                          ButtonSegment(value: 2, label: Text('Medium'), icon: Icon(Icons.sentiment_neutral)),
                          ButtonSegment(value: 3, label: Text('Hard'), icon: Icon(Icons.psychology)),
                        ],
                        selected: {_difficulty},
                        onSelectionChanged: (s) => setState(() => _difficulty = s.first),
                      ),
                    ),
                    Expanded(
                      child: ListView.builder(
                        padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                        itemCount: _packs?.length ?? 0,
                        itemBuilder: (context, index) {
                          final pack = _packs![index];
                          return Card(
                            elevation: 3,
                            margin: const EdgeInsets.only(bottom: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                            child: ListTile(
                              contentPadding: const EdgeInsets.all(16),
                              leading: CircleAvatar(
                                radius: 28,
                                backgroundColor: Colors.teal.shade100,
                                child: const Icon(Icons.celebration, color: Colors.teal, size: 30),
                              ),
                              title: Text(pack.name,
                                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                              subtitle: Text(
                                '${pack.region} • ${pack.itemCount} items\n${pack.description}',
                                style: const TextStyle(fontSize: 15),
                              ),
                              isThreeLine: true,
                              trailing: const Icon(Icons.chevron_right, size: 36),
                              onTap: () => _start(pack),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
    );
  }
}
