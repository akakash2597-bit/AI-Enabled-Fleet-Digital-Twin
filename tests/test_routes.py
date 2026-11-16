import unittest
from app import create_app

class RouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_home_page(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"FleetTwin", res.data)

    def test_dashboard_page(self):
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Fleet Operations Digital Twin Dashboard", res.data)

    def test_vehicle_list_page(self):
        res = self.client.get('/vehicles')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"VH-101", res.data)

    def test_vehicle_detail_twin(self):
        res = self.client.get('/vehicles/VH-101')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Subsystem Digital Twin Virtualization", res.data)

    def test_predictions_page(self):
        res = self.client.get('/predictions')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Predictive Maintenance & Failure Risk Alerts", res.data)

    def test_api_predict(self):
        payload = {
            'Engine rpm': 800,
            'Coolant temp': 78.0,
            'Lub oil pressure': 3.5,
            'lub oil temp': 76.0,
            'Fuel pressure': 6.2,
            'Coolant pressure': 2.3
        }
        res = self.client.post('/api/predict', json=payload)
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertIn('prediction', json_data)
        self.assertIn('failure_risk_score', json_data['prediction'])

if __name__ == '__main__':
    unittest.main()
