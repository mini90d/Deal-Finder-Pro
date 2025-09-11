import 'dart:math';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:arcore_flutter_plugin/arcore_flutter_plugin.dart';
import 'package:vector_math/vector_math_64.dart';
import 'package:camera/camera.dart';
import '../services/deal_service.dart';
import '../models/deal.dart';
import './deal_details_screen.dart';

class ARDealHuntScreen extends StatefulWidget {
  final List<CameraDescription> cameras;

  const ARDealHuntScreen({super.key, required this.cameras});

  @override
  ARDealHuntScreenState createState() => ARDealHuntScreenState();
}

class ARDealHuntScreenState extends State<ARDealHuntScreen> {
  late ArCoreController arCoreController;
  List<Deal> _arDeals = [];
  bool _isLoading = true;

  @override
  void dispose() {
    arCoreController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AR Deal Hunt')),
      body: Stack(
        children: [
          ArCoreView(
            onArCoreViewCreated: _onArCoreViewCreated,
            enableTapRecognizer: true,
          ),
          if (_isLoading)
            const Center(child: CircularProgressIndicator()),
        ],
      ),
    );
  }

  void _onArCoreViewCreated(ArCoreController controller) {
    arCoreController = controller;
    arCoreController.onNodeTap = (name) => _onNodeTapped(name);
    _fetchAndSpawnDeals();
  }

  Future<void> _fetchAndSpawnDeals() async {
    final dealService = Provider.of<DealService>(context, listen: false);
    // Hardcoded location near a sample deal (New York City)
    final deals = await dealService.fetchArDeals(40.7128, -74.0060);

    if (!mounted) return;

    setState(() {
      _arDeals = deals;
      _isLoading = false;
    });

    if (_arDeals.isNotEmpty) {
      _spawnDealNodes();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No nearby deals found.')),
      );
    }
  }

  void _spawnDealNodes() {
    final random = Random();
    for (final deal in _arDeals) {
      final node = ArCoreNode(
        name: deal.id,
        shape: ArCoreCylinder(
          materials: [ArCoreMaterial(color: Colors.yellow, metallic: 1.0)],
          radius: 0.2,
          height: 0.05,
        ),
        position: Vector3(
          random.nextDouble() * 4 - 2, // x: -2.0 to 2.0
          random.nextDouble() * 2 - 1, // y: -1.0 to 1.0
          -random.nextDouble() * 3 - 2, // z: -2.0 to -5.0
        ),
      );
      arCoreController.addArCoreNode(node);
    }
  }

  void _onNodeTapped(String nodeName) {
    final tappedDeal = _arDeals.firstWhere((d) => d.id == nodeName);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('${tappedDeal.name} at ${tappedDeal.businessName}'),
        action: SnackBarAction(
          label: 'VIEW',
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => DealDetailsScreen(deal: tappedDeal),
              ),
            );
          },
        ),
      ),
    );
  }
}
