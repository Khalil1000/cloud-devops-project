import base64
import json
import unittest
from scripts.lambda_smoke import validate_response


class LambdaResponseTests(unittest.TestCase):
    def test_api_success_does_not_hide_function_failure(self):
        with self.assertRaises(ValueError):
            validate_response({"StatusCode": 200, "FunctionError": "Unhandled"}, {}, "/version", "v1")

    def test_application_500_fails_even_without_lambda_function_error(self):
        with self.assertRaises(ValueError):
            validate_response({"StatusCode": 200}, {"statusCode": 500}, "/version", "v1")

    def test_wrong_release_fails(self):
        with self.assertRaises(ValueError):
            validate_response({"StatusCode": 200}, {"statusCode": 200, "body": '{"version":"old"}'}, "/version", "new")

    def test_base64_response_can_identify_release(self):
        body = base64.b64encode(json.dumps({"version": "v1"}).encode()).decode()
        validate_response({"StatusCode": 200}, {"statusCode": 200, "body": body, "isBase64Encoded": True}, "/version", "v1")
