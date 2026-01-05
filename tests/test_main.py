import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, validate_crypto_code


class TestValidateCryptoCode(unittest.TestCase):
    """Test the validate_crypto_code function"""
    
    def test_valid_crypto_codes(self):
        """Test valid cryptocurrency codes"""
        self.assertTrue(validate_crypto_code("BTC"))
        self.assertTrue(validate_crypto_code("ETH"))
        self.assertTrue(validate_crypto_code("SOL"))
        self.assertTrue(validate_crypto_code("btc"))  # Should handle lowercase
        self.assertTrue(validate_crypto_code("ADA"))
        self.assertTrue(validate_crypto_code("XRP"))
        self.assertTrue(validate_crypto_code("DOGE"))
        # Codes with numbers but containing letters
        self.assertTrue(validate_crypto_code("A1"))
        self.assertTrue(validate_crypto_code("B2C"))
    
    def test_invalid_crypto_codes(self):
        """Test invalid cryptocurrency codes"""
        self.assertFalse(validate_crypto_code(""))
        self.assertFalse(validate_crypto_code("B"))  # Too short (1 char)
        self.assertFalse(validate_crypto_code("BTC!"))
        self.assertFalse(validate_crypto_code("BT-C"))
        self.assertFalse(validate_crypto_code("TOOLONGCODE123"))  # > 5 chars
        self.assertFalse(validate_crypto_code("BTC ETH"))  # Contains space
        self.assertFalse(validate_crypto_code("123"))  # Pure numbers (no letters)
        self.assertFalse(validate_crypto_code("1234"))  # Pure numbers (no letters)
        self.assertFalse(validate_crypto_code("A1B2C3"))  # Too long (6 chars)


class TestCryptocurrencyEndpoint(unittest.TestCase):    
    """Test the /cryptocurrency/{crypto_code}/ endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    @patch('main.requests.get')
    def test_successful_request(self, mock_get):
        """Test successful cryptocurrency price request"""
        # Mock API response for each currency
        mock_responses = []
        currencies = ["USD", "EUR", "BRL", "GBP", "AUD"]
        
        for currency in currencies:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "status": {"error_code": 0},
                "data": {
                    "BTC": {
                        "quote": {
                            currency: {
                                "price": 50000.0 if currency == "USD" else 45000.0
                            }
                        }
                    }
                }
            }
            mock_response.raise_for_status = MagicMock()
            mock_responses.append(mock_response)
        
        mock_get.side_effect = mock_responses
        
        response = self.client.get("/cryptocurrency/BTC/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("USD", data)
        self.assertIn("EUR", data)
        self.assertIn("BRL", data)
        self.assertIn("GBP", data)
        self.assertIn("AUD", data)
    
    def test_invalid_crypto_code_format(self):
        """Test invalid cryptocurrency code format"""
        response = self.client.get("/cryptocurrency/BTC!/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid cryptocurrency code", response.json()["detail"])
    
    def test_invalid_crypto_code_with_space(self):
        """Test cryptocurrency code with space"""
        response = self.client.get("/cryptocurrency/BTC ETH/")
        self.assertEqual(response.status_code, 400)
    
    @patch('main.requests.get')
    def test_cryptocurrency_not_found(self, mock_get):
        """Test when cryptocurrency is not found"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": {"error_code": 0},
            "data": {}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        response = self.client.get("/cryptocurrency/INVALID/")
        self.assertEqual(response.status_code, 404)
    
    @patch('main.requests.get')
    def test_api_error_response(self, mock_get):
        """Test API error response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": {
                "error_code": 400,
                "error_message": "Invalid API key"
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        response = self.client.get("/cryptocurrency/BTC/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("CoinMarketCap API error", response.json()["detail"])
    
    @patch('main.requests.get')
    def test_network_error(self, mock_get):
        """Test network error handling - all requests fail"""
        import requests
        # Make all requests fail (5 currencies = 5 requests)
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        response = self.client.get("/cryptocurrency/BTC/")
        # When all requests fail, all_prices will have None values
        # The code should check if all values are None and return 404
        # Current code returns 200 with None values, but we want 404
        # So we need to fix the code OR test for actual behavior
        # For now, test that it returns 404 (expected behavior)
        self.assertEqual(response.status_code, 404)


class TestAppStructure(unittest.TestCase):
    """Test basic app structure"""
    
    def test_app_exists(self):
        """Test that app is created"""
        self.assertIsNotNone(app)
    
    def test_app_title(self):
        """Test app has title"""
        # FastAPI apps have title attribute
        self.assertTrue(hasattr(app, 'title'))


if __name__ == '__main__':
    unittest.main()

