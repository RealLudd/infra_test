#!/usr/bin/env python3
"""
Simple test script to verify all dashboard API endpoints work correctly
"""

import sys
import requests
import json
from app import app

def test_endpoints():
    """Test all API endpoints"""
    test_results = []

    with app.test_client() as client:
        # Test main page
        print("Testing main dashboard page...")
        response = client.get('/')
        test_results.append({
            'endpoint': '/',
            'status': response.status_code,
            'success': response.status_code == 200
        })

        # Test overview endpoint with different periods
        periods = ['today', 'week', 'month', 'quarter']
        for period in periods:
            print(f"Testing /api/overview?period={period}...")
            response = client.get(f'/api/overview?period={period}')
            data = response.get_json()
            test_results.append({
                'endpoint': f'/api/overview?period={period}',
                'status': response.status_code,
                'success': response.status_code == 200 and data is not None,
                'data_keys': list(data.keys()) if data else []
            })

        # Test automation trend
        print("Testing /api/automation-trend...")
        response = client.get('/api/automation-trend?period=week')
        data = response.get_json()
        test_results.append({
            'endpoint': '/api/automation-trend',
            'status': response.status_code,
            'success': response.status_code == 200 and data is not None,
            'has_labels': 'labels' in data if data else False,
            'has_data': 'data' in data if data else False
        })

        # Test automation efficiency
        print("Testing /api/automation-efficiency...")
        response = client.get('/api/automation-efficiency')
        data = response.get_json()
        test_results.append({
            'endpoint': '/api/automation-efficiency',
            'status': response.status_code,
            'success': response.status_code == 200 and data is not None,
            'data_keys': list(data.keys()) if data else []
        })

        # Test exceptions
        print("Testing /api/exceptions...")
        response = client.get('/api/exceptions')
        data = response.get_json()
        test_results.append({
            'endpoint': '/api/exceptions',
            'status': response.status_code,
            'success': response.status_code == 200 and data is not None,
            'data_keys': list(data.keys()) if data else []
        })

        # Test remittance insights
        print("Testing /api/remittance-insights...")
        response = client.get('/api/remittance-insights')
        data = response.get_json()
        test_results.append({
            'endpoint': '/api/remittance-insights',
            'status': response.status_code,
            'success': response.status_code == 200 and data is not None,
            'data_keys': list(data.keys()) if data else []
        })

        # Test month-end summary
        print("Testing /api/month-end-summary...")
        response = client.get('/api/month-end-summary')
        data = response.get_json()
        test_results.append({
            'endpoint': '/api/month-end-summary',
            'status': response.status_code,
            'success': response.status_code == 200 and data is not None,
            'data_keys': list(data.keys()) if data else []
        })

    return test_results

def print_results(results):
    """Print test results in a readable format"""
    print("\n" + "="*60)
    print("DASHBOARD API TEST RESULTS")
    print("="*60 + "\n")

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])

    for result in results:
        status_symbol = "✓" if result['success'] else "✗"
        print(f"{status_symbol} {result['endpoint']}")
        print(f"  Status Code: {result['status']}")
        if 'data_keys' in result:
            print(f"  Data Keys: {', '.join(result['data_keys'])}")
        if 'has_labels' in result:
            print(f"  Has Labels: {result['has_labels']}")
        if 'has_data' in result:
            print(f"  Has Data: {result['has_data']}")
        print()

    print("="*60)
    print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
    print("="*60)

    return passed_tests == total_tests

if __name__ == '__main__':
    try:
        results = test_endpoints()
        all_passed = print_results(results)
        sys.exit(0 if all_passed else 1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
