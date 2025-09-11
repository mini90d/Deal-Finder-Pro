const express = require('express');
const mongoose = require('mongoose');
const Deal = require('./models/deal');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Database connection
mongoose.connect('mongodb://localhost:27017/dealfinder', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('MongoDB connected...'))
.catch(err => console.log(err));

// Routes
app.get('/', (req, res) => {
  res.send('Deal Finder Pro API is running...');
});

// GET /api/deals - Get all deals, sorted by discount
app.get('/api/deals', async (req, res) => {
  try {
    const deals = await Deal.find()
      .sort({ discountPercentage: -1 })
      .limit(50);
    res.json(deals);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// POST /api/deals/ar - Get deals near a location
app.post('/api/deals/ar', async (req, res) => {
  const { latitude, longitude } = req.body;

  if (!latitude || !longitude) {
    return res.status(400).json({ msg: 'Please provide latitude and longitude' });
  }

  try {
    const nearbyDeals = await Deal.find({
      location: {
        $near: {
          $geometry: {
            type: "Point",
            coordinates: [longitude, latitude]
          },
          $maxDistance: 5000 // 5 kilometers
        }
      }
    });
    res.json(nearbyDeals);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// GET /api/deals/recommended - Get AI-powered recommendations
app.get('/api/deals/recommended', async (req, res) => {
  try {
    // Find the most recently added deal to simulate a "view history"
    const lastDeal = await Deal.findOne().sort({ createdAt: -1 });

    let recommendedDeals = [];

    if (lastDeal && lastDeal.tags.length > 0) {
      const primaryTag = lastDeal.tags[0];
      // Find other deals with the same primary tag, excluding the last deal itself
      recommendedDeals = await Deal.find({
        tags: primaryTag,
        _id: { $ne: lastDeal._id },
      }).limit(10);
    }

    // If no recommendations are found, fall back to the highest discount deals
    if (recommendedDeals.length === 0) {
      recommendedDeals = await Deal.find()
        .sort({ discountPercentage: -1 })
        .limit(5);
    }

    res.json(recommendedDeals);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
