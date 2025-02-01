// main.dart (Complete)
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:camera/camera.dart';
import 'screens/home_screen.dart';
import 'services/deal_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => DealService()),
      ],
      child: DealFinderApp(cameras: cameras),
    ),
  );
}

class DealFinderApp extends StatelessWidget {
  final List<CameraDescription> cameras;

  const DealFinderApp({super.key, required this.cameras});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Deal Finder Pro',
      theme: ThemeData.dark(),
      home: HomeScreen(cameras: cameras),
    );
  }
}
