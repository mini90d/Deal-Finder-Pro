const mongoose = require('mongoose');
const Deal = require('./models/deal');

const MONGO_URI = 'mongodb://localhost:27017/dealfinder';

const sampleDeals = [
  {
    name: '50% Off Large Pizzas',
    description: 'Get 50% off any large pizza at Pizza Palace. Toppings extra.',
    discountPercentage: 50,
    originalPrice: 20.00,
    businessName: 'Pizza Palace',
    imageUrl: 'https://via.placeholder.com/150/FFC107/000000?Text=Pizza',
    tags: ['food', 'pizza', 'restaurant'],
    location: { type: 'Point', coordinates: [-74.0060, 40.7128] } // New York City
  },
  {
    name: '2-for-1 Movie Tickets',
    description: 'Buy one movie ticket and get the second one free. Valid for all shows.',
    discountPercentage: 50,
    businessName: 'Cinema World',
    imageUrl: 'https://via.placeholder.com/150/03A9F4/FFFFFF?Text=Movies',
    tags: ['entertainment', 'movies'],
    location: { type: 'Point', coordinates: [-118.2437, 34.0522] } // Los Angeles
  },
  {
    name: '30% Off All Electronics',
    description: 'Save 30% on all electronics, including TVs, laptops, and headphones.',
    discountPercentage: 30,
    businessName: 'ElectroZone',
    imageUrl: 'https://via.placeholder.com/150/4CAF50/FFFFFF?Text=Electronics',
    tags: ['electronics', 'shopping'],
    location: { type: 'Point', coordinates: [-87.6298, 41.8781] } // Chicago
  },
  {
    name: 'Free Coffee with Breakfast',
    description: 'Get a free coffee of any size with the purchase of any breakfast entree.',
    discountPercentage: 15, // Approximate value
    businessName: 'The Daily Grind',
    imageUrl: 'https://via.placeholder.com/150/E91E63/FFFFFF?Text=Coffee',
    tags: ['food', 'coffee', 'cafe'],
    location: { type: 'Point', coordinates: [-122.4194, 37.7749] } // San Francisco
  }
];

const seedDatabase = async () => {
  try {
    await mongoose.connect(MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('MongoDB connected for seeding...');

    await Deal.deleteMany({});
    console.log('Existing deals deleted.');

    await Deal.insertMany(sampleDeals);
    console.log('Sample deals inserted.');

  } catch (err) {
    console.error(err.message);
    process.exit(1);
  } finally {
    mongoose.connection.close();
    console.log('MongoDB connection closed.');
  }
};

seedDatabase();
