-- SQL schema for Supabase database
-- Run these commands in your Supabase SQL editor

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create crypto_assets table
CREATE TABLE crypto_assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    current_price DECIMAL(20, 8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create portfolio table
CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES crypto_assets(id) ON DELETE CASCADE,
    quantity DECIMAL(20, 8) NOT NULL,
    purchase_price DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_portfolio_user_id ON portfolio(user_id);
CREATE INDEX idx_portfolio_asset_id ON portfolio(asset_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_crypto_assets_symbol ON crypto_assets(symbol);

-- Insert some sample crypto assets
INSERT INTO crypto_assets (symbol, name, current_price) VALUES
('BTC', 'Bitcoin', 45000.00),
('ETH', 'Ethereum', 3000.00),
('ADA', 'Cardano', 0.50),
('DOT', 'Polkadot', 25.00),
('SOL', 'Solana', 100.00);
