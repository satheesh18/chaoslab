#!/bin/bash

# Test script for Flask app endpoints

BASE_URL="http://localhost:5000"

echo "🧪 Testing Flask Test App Endpoints"
echo "===================================="
echo ""

# Health check
echo "1. Testing /health..."
curl -s $BASE_URL/health | jq '.'
echo ""

# Data endpoint
echo "2. Testing /api/data..."
curl -s $BASE_URL/api/data | jq '.'
echo ""

# Heavy operation
echo "3. Testing /api/heavy..."
curl -s $BASE_URL/api/heavy | jq '.'
echo ""

# Memory operation
echo "4. Testing /api/memory..."
curl -s $BASE_URL/api/memory | jq '.'
echo ""

# Database simulation
echo "5. Testing /api/database..."
curl -s $BASE_URL/api/database | jq '.'
echo ""

# Network simulation
echo "6. Testing /api/network..."
curl -s $BASE_URL/api/network | jq '.'
echo ""

# Stress test
echo "7. Testing /api/stress..."
curl -s $BASE_URL/api/stress | jq '.'
echo ""

echo "✅ All tests completed!"
