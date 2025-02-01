// ar_deal_hunt_screen.dart
import 'package:flutter/material.dart';
import 'package:arcore_flutter_plugin/arcore_flutter_plugin.dart';

class ARDealHuntScreen extends StatefulWidget {
  final List<CameraDescription> cameras;
  
  const ARDealHuntScreen({super.key, required this.cameras});

  @override
  ARDealHuntScreenState createState() => ARDealHuntScreenState();
}

class ARDealHuntScreenState extends State<ARDealHuntScreen> {
  late ArCoreController arCoreController;

  @override
  void dispose() {
    arCoreController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AR Deal Hunt')),
      body: ArCoreView(
        onArCoreViewCreated: _onArCoreViewCreated,
      ),
    );
  }

  void _onArCoreViewCreated(ArCoreController controller) {
    arCoreController = controller;
    _addDealObjects();
  }

  void _addDealObjects() {
    // AR object spawning logic
    final node = ArCoreNode(
      shape: ArCoreSphere(
        materials: [ArCoreMaterial(color: Colors.blue)],
      ),
      position: Vector3(0, 0, -1.5),
    );
    arCoreController.addArCoreNode(node);
  }
}
