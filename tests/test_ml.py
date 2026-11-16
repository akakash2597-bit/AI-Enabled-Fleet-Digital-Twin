import unittest
from app.services.predictor import predictor
from app.services.digital_twin import get_digital_twin

class MLTestCase(unittest.TestCase):
    def test_ml_predictor_loaded(self):
        self.assertIsNotNone(predictor.model)
        self.assertIsNotNone(predictor.scaler)

    def test_ml_prediction_inference(self):
        reading = {
            'Engine rpm': 750,
            'Coolant temp': 78.0,
            'Lub oil pressure': 3.2,
            'lub oil temp': 77.0,
            'Fuel pressure': 6.5,
            'Coolant pressure': 2.3
        }
        result = predictor.predict(reading)
        self.assertIn('failure_predicted', result)
        self.assertIn('failure_risk_score', result)
        self.assertIn('severity', result)
        self.assertIn('suspect_component', result)
        self.assertTrue(0.0 <= result['failure_risk_score'] <= 1.0)

    def test_digital_twin_computation(self):
        twin = get_digital_twin('VH-TEST')
        state = twin.compute_twin_state({
            'Engine rpm': 800,
            'Coolant temp': 135.0,
            'Lub oil pressure': 1.0,
            'lub oil temp': 88.0,
            'Fuel pressure': 6.0,
            'Coolant pressure': 0.8
        })
        self.assertLess(state['overall_health_score'], 80)
        self.assertIn(state['subsystems']['cooling_system']['status'], ('Warning', 'Critical'))

if __name__ == '__main__':
    unittest.main()
