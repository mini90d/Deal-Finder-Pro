// server.js
const express = require('express');
const mongoose = require('mongoose');
const Deal = require('./models/deal');

const app = express();
mongoose.connect('mongodb://localhost:27017/dealfinder');

app.get('/api/deals', async (req, res) => {
  const deals = await Deal.find()
    .sort({ discountPercentage: -1 })
    .limit(50);
  res.json(deals);
});

app.post('/api/deals/ar', async (req, res) => {
  const { latitude, longitude } = req.body;
  const nearbyDeals = await Deal.find({
    location: {
      $near: {
        $geometry: {
          type: "Point",
          coordinates: [longitude, latitude]
        },
        $maxDistance: 5000
      }
    }
  });
  res.json(nearbyDeals);
});
