import 'package:flutter/material.dart';
import '../models/deal.dart';

class DealDetailsScreen extends StatelessWidget {
  final Deal deal;

  const DealDetailsScreen({super.key, required this.deal});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(deal.name),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (deal.imageUrl != null)
              Center(
                child: Image.network(
                  deal.imageUrl!,
                  fit: BoxFit.cover,
                  height: 250,
                  width: double.infinity,
                  errorBuilder: (context, error, stackTrace) {
                    return Container(
                      height: 250,
                      color: Colors.grey[800],
                      child: const Center(
                        child: Icon(
                          Icons.local_offer,
                          color: Colors.grey,
                          size: 60,
                        ),
                      ),
                    );
                  },
                ),
              ),
            const SizedBox(height: 16),
            Text(
              deal.name,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'at ${deal.businessName}',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.grey[400]),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Text(
                  '${deal.discountPercentage.toStringAsFixed(0)}% OFF',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: Colors.green,
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(width: 16),
                if (deal.originalPrice != null && deal.discountedPrice != null)
                  Text(
                    '\$${deal.originalPrice!.toStringAsFixed(2)}',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          decoration: TextDecoration.lineThrough,
                          color: Colors.grey,
                        ),
                  ),
                const SizedBox(width: 8),
                if (deal.discountedPrice != null)
                Text(
                  '\$${deal.discountedPrice!.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                )
              ],
            ),
            const SizedBox(height: 24),
            const Divider(),
            const SizedBox(height: 16),
            Text(
              'Description',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              deal.description,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 16),
            if (deal.tags.isNotEmpty) ...[
              Text(
                'Tags',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8.0,
                children: deal.tags.map((tag) => Chip(label: Text(tag))).toList(),
              ),
            ]
          ],
        ),
      ),
    );
  }
}
