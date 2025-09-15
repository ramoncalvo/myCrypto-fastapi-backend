// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the mycrypto database
db = db.getSiblingDB('mycrypto');

// Create collections with validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'name'],
      properties: {
        email: {
          bsonType: 'string',
          description: 'User email - required and must be a string'
        },
        name: {
          bsonType: 'string',
          description: 'User name - required and must be a string'
        },
        password: {
          bsonType: 'string',
          description: 'User password - must be a string'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});

db.createCollection('crypto_assets', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['symbol', 'name'],
      properties: {
        symbol: {
          bsonType: 'string',
          description: 'Asset symbol - required and must be a string'
        },
        name: {
          bsonType: 'string',
          description: 'Asset name - required and must be a string'
        },
        current_price: {
          bsonType: 'number',
          minimum: 0,
          description: 'Current price - must be a positive number'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});

db.createCollection('portfolio', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'asset_id', 'quantity'],
      properties: {
        user_id: {
          bsonType: 'string',
          description: 'User ID - required and must be a string'
        },
        asset_id: {
          bsonType: 'string',
          description: 'Asset ID - required and must be a string'
        },
        quantity: {
          bsonType: 'number',
          minimum: 0,
          description: 'Asset quantity - must be a positive number'
        },
        purchase_price: {
          bsonType: 'number',
          minimum: 0,
          description: 'Purchase price - must be a positive number'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.crypto_assets.createIndex({ "symbol": 1 }, { unique: true });
db.portfolio.createIndex({ "user_id": 1 });
db.portfolio.createIndex({ "asset_id": 1 });
db.portfolio.createIndex({ "user_id": 1, "asset_id": 1 });

// Insert sample data for testing
// Note: Users will be created via API registration to ensure proper password hashing
// These are just placeholder crypto assets and portfolio data

db.crypto_assets.insertMany([
  {
    symbol: "BTC",
    name: "Bitcoin",
    current_price: 45000.00,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    symbol: "ETH",
    name: "Ethereum",
    current_price: 3000.00,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    symbol: "ADA",
    name: "Cardano",
    current_price: 0.50,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    symbol: "DOT",
    name: "Polkadot",
    current_price: 25.00,
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print('MongoDB initialization completed successfully!');
print('Collections created: users, crypto_assets, portfolio');
print('Sample data inserted for testing');
print('Indexes created for optimal performance');
