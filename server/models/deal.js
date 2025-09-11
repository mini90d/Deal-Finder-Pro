const mongoose = require('mongoose');

const dealSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true,
  },
  description: {
    type: String,
    required: true,
  },
  discountPercentage: {
    type: Number,
    required: true,
    min: 0,
    max: 100,
  },
  originalPrice: {
    type: Number,
    required: false,
  },
  businessName: {
    type: String,
    required: true,
  },
  imageUrl: {
    type: String,
    required: false,
  },
  tags: [String],
  location: {
    type: {
      type: String,
      enum: ['Point'],
      required: true
    },
    coordinates: {
      type: [Number],
      required: true
    }
  }
}, {
  timestamps: true,
  toJSON: {
    virtuals: true,
    transform: (doc, ret) => {
      delete ret._id;
      delete ret.__v;
    }
  }
});

dealSchema.index({ location: '2dsphere' });

// Virtual for discountedPrice
dealSchema.virtual('discountedPrice').get(function() {
  if (this.originalPrice) {
    return this.originalPrice * (1 - this.discountPercentage / 100);
  }
  return null;
});

const Deal = mongoose.model('Deal', dealSchema);

module.exports = Deal;
