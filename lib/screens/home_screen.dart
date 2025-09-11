import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/deal_service.dart';
import '../models/deal.dart';
import './ar_deal_hunt_screen.dart';
import './deal_details_screen.dart';

class HomeScreen extends StatefulWidget {
  final cameras; // just to pass it to the AR screen
  const HomeScreen({super.key, this.cameras});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final dealService = Provider.of<DealService>(context, listen: false);
      dealService.fetchDeals();
      dealService.fetchRecommendedDeals();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Deal Finder Pro'),
        actions: [
          IconButton(
            icon: const Icon(Icons.camera_alt_outlined),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => ARDealHuntScreen(cameras: widget.cameras),
                ),
              );
            },
          ),
        ],
      ),
      body: Consumer<DealService>(
        builder: (context, dealService, child) {
          if (dealService.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (dealService.error != null) {
            return Center(child: Text('Error: ${dealService.error}'));
          }

          if (dealService.deals.isEmpty) {
            return const Center(child: Text('No deals found.'));
          }

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildRecommendedSection(dealService),
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'All Deals',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
              ),
              Expanded(
                child: ListView.builder(
                  itemCount: dealService.deals.length,
                  itemBuilder: (context, index) {
                    final deal = dealService.deals[index];
                    return ListTile(
                      leading: deal.imageUrl != null
                          ? AspectRatio(
                              aspectRatio: 1,
                              child: Image.network(
                                deal.imageUrl!,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) {
                                  return const Icon(Icons.local_offer);
                                },
                              ),
                            )
                          : const Icon(Icons.local_offer),
                      title: Text(deal.name),
                      subtitle: Text(deal.businessName),
                      trailing: Text(
                        '${deal.discountPercentage.toStringAsFixed(0)}% OFF',
                        style: const TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => DealDetailsScreen(deal: deal),
                          ),
                        );
                      },
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildRecommendedSection(DealService dealService) {
    if (dealService.recommendedDeals.isEmpty) {
      return const SizedBox.shrink(); // Return an empty widget if no recommendations
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(16.0, 16.0, 16.0, 8.0),
          child: Text(
            'Recommended For You',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
        ),
        SizedBox(
          height: 220,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: dealService.recommendedDeals.length,
            itemBuilder: (context, index) {
              final deal = dealService.recommendedDeals[index];
              return RecommendedDealCard(deal: deal);
            },
          ),
        ),
        const Divider(),
      ],
    );
  }
}

class RecommendedDealCard extends StatelessWidget {
  final Deal deal;
  const RecommendedDealCard({super.key, required this.deal});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => DealDetailsScreen(deal: deal),
          ),
        );
      },
      child: Container(
        width: 180,
        margin: const EdgeInsets.all(8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (deal.imageUrl != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(8.0),
                child: Image.network(
                  deal.imageUrl!,
                  height: 120,
                  width: double.infinity,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    return const Center(
                      child: Icon(
                        Icons.local_offer,
                        color: Colors.grey,
                        size: 40,
                      ),
                    );
                  },
                ),
              ),
            Padding(
              padding: const EdgeInsets.fromLTRB(4.0, 8.0, 4.0, 4.0),
              child: Text(
                deal.name,
                style: const TextStyle(fontWeight: FontWeight.bold),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4.0),
              child: Text(
                deal.businessName,
                style: const TextStyle(color: Colors.grey),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
