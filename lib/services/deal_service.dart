import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/deal.dart';

class DealService extends ChangeNotifier {
  static const String _baseUrl = 'http://localhost:3000/api';

  List<Deal> _deals = [];
  List<Deal> get deals => _deals;

  List<Deal> _recommendedDeals = [];
  List<Deal> get recommendedDeals => _recommendedDeals;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _error;
  String? get error => _error;

  Future<void> fetchDeals() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await http.get(Uri.parse('$_baseUrl/deals'));

      if (response.statusCode == 200) {
        final List<dynamic> dealJson = json.decode(response.body);
        _deals = dealJson.map((json) => Deal.fromJson(json)).toList();
      } else {
        _error = 'Failed to load deals: ${response.statusCode}';
      }
    } catch (e) {
      _error = 'Failed to load deals: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchRecommendedDeals() async {
    // This can be run in the background without setting a global loading state
    try {
      final response = await http.get(Uri.parse('$_baseUrl/deals/recommended'));

      if (response.statusCode == 200) {
        final List<dynamic> dealJson = json.decode(response.body);
        _recommendedDeals = dealJson.map((json) => Deal.fromJson(json)).toList();
        notifyListeners(); // Notify listeners to update the UI
      }
    } catch (e) {
      // Silently fail for now, as this is a non-critical feature for the UI
      print('Failed to load recommended deals: $e');
    }
  }

  Future<List<Deal>> fetchArDeals(double latitude, double longitude) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/deals/ar'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'latitude': latitude, 'longitude': longitude}),
      );

      if (response.statusCode == 200) {
        final List<dynamic> dealJson = json.decode(response.body);
        return dealJson.map((json) => Deal.fromJson(json)).toList();
      } else {
        // Handle error, maybe return an empty list or throw an exception
        return [];
      }
    } catch (e) {
      // Handle error
      return [];
    }
  }
}
