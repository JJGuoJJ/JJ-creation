"""Backend API Testing for Personal Investment Bank System"""
import requests
import sys
import json
from datetime import datetime

class PIBAPITester:
    def __init__(self, base_url="https://tech-portfolio-502.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.critical_failures = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, check_fields=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {method} {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
            else:
                print(f"❌ Unsupported method: {method}")
                return False, {}

            success = response.status_code == expected_status
            
            if success:
                try:
                    resp_json = response.json()
                    
                    # Check required fields if specified
                    if check_fields:
                        for field in check_fields:
                            if field not in resp_json:
                                print(f"⚠️  Warning: Missing field '{field}' in response")
                                success = False
                    
                    if success:
                        self.tests_passed += 1
                        print(f"✅ Passed - Status: {response.status_code}")
                        if check_fields:
                            print(f"   Fields present: {', '.join(check_fields)}")
                    else:
                        self.failed_tests.append(name)
                        print(f"❌ Failed - Missing required fields")
                    
                    return success, resp_json
                except Exception as e:
                    print(f"⚠️  Response not JSON: {e}")
                    return success, {}
            else:
                self.failed_tests.append(name)
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.text[:200]}")
                except:
                    pass
                return False, {}

        except requests.exceptions.Timeout:
            self.failed_tests.append(name)
            self.critical_failures.append(f"{name}: Timeout")
            print(f"❌ Failed - Request timeout (>30s)")
            return False, {}
        except Exception as e:
            self.failed_tests.append(name)
            self.critical_failures.append(f"{name}: {str(e)}")
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health(self):
        """U1: GET /api/health"""
        success, response = self.run_test(
            "U1: Health Check",
            "GET",
            "api/health",
            200,
            check_fields=["status", "last_data_date", "pipeline_running"]
        )
        if success:
            print(f"   Last data date: {response.get('last_data_date')}")
            print(f"   Pipeline running: {response.get('pipeline_running')}")
        return success, response

    def test_market_overview(self):
        """U2: GET /api/market/overview"""
        success, response = self.run_test(
            "U2: Market Overview",
            "GET",
            "api/market/overview",
            200,
            check_fields=["regime", "regime_cn", "global_fng", "china_tech_fng", "allocation"]
        )
        if success:
            print(f"   Regime: {response.get('regime')} ({response.get('regime_cn')})")
            print(f"   Global F&G: {response.get('global_fng')}")
            print(f"   China Tech F&G: {response.get('china_tech_fng')}")
            alloc = response.get('allocation', {})
            print(f"   Allocation bands: equity={alloc.get('equity')}, ai_tech={alloc.get('ai_tech')}, cash={alloc.get('cash')}")
            
            # Check if allocation is not empty
            if not alloc or all(not v for v in alloc.values()):
                print(f"⚠️  Warning: Allocation is empty (pipeline may not have run)")
        return success, response

    def test_sectors(self):
        """U3: GET /api/sectors"""
        success, response = self.run_test(
            "U3: Sectors",
            "GET",
            "api/sectors",
            200,
            check_fields=["sectors"]
        )
        if success:
            sectors = response.get('sectors', [])
            print(f"   Found {len(sectors)} sectors")
            if len(sectors) > 0:
                sample = sectors[0]
                print(f"   Sample: {sample.get('sector')} - heat={sample.get('heat_score')}, momentum={sample.get('momentum')}, action={sample.get('action')}")
            else:
                print(f"⚠️  Warning: No sectors returned (pipeline may not have run)")
        return success, response

    def test_watchlist(self):
        """U4: GET /api/watchlist (with filters)"""
        # Test without filters
        success, response = self.run_test(
            "U4a: Watchlist (no filter)",
            "GET",
            "api/watchlist",
            200,
            check_fields=["recommendations"]
        )
        if success:
            recs = response.get('recommendations', [])
            print(f"   Found {len(recs)} recommendations")
            if len(recs) > 0:
                sample = recs[0]
                print(f"   Sample: {sample.get('symbol')} - {sample.get('name')} - action={sample.get('action')}")
        
        # Test with sector filter
        success2, response2 = self.run_test(
            "U4b: Watchlist (sector filter)",
            "GET",
            "api/watchlist",
            200,
            params={"sector": "AI芯片"},
            check_fields=["recommendations"]
        )
        
        # Test with market filter
        success3, response3 = self.run_test(
            "U4c: Watchlist (market=CN)",
            "GET",
            "api/watchlist",
            200,
            params={"market": "CN"},
            check_fields=["recommendations"]
        )
        
        # Test with action filter
        success4, response4 = self.run_test(
            "U4d: Watchlist (action filter)",
            "GET",
            "api/watchlist",
            200,
            params={"action": "Hold"},
            check_fields=["recommendations"]
        )
        
        return success and success2 and success3 and success4, response

    def test_recommendations_today(self):
        """U5: GET /api/recommendations/today"""
        success, response = self.run_test(
            "U5: Recommendations Today",
            "GET",
            "api/recommendations/today",
            200,
            check_fields=["recommendations"]
        )
        if success:
            recs = response.get('recommendations', [])
            print(f"   Found {len(recs)} top recommendations")
            if len(recs) > 0:
                for i, rec in enumerate(recs[:3]):
                    print(f"   {i+1}. {rec.get('symbol')} - {rec.get('name')} - score={rec.get('score')}, action={rec.get('action')} ({rec.get('action_cn')})")
        return success, response

    def test_portfolio(self):
        """U6: GET /api/portfolio and /api/portfolio/diagnose"""
        success, response = self.run_test(
            "U6a: Portfolio",
            "GET",
            "api/portfolio",
            200,
            check_fields=["positions"]
        )
        if success:
            positions = response.get('positions', [])
            print(f"   Found {len(positions)} positions")
        
        success2, response2 = self.run_test(
            "U6b: Portfolio Diagnose",
            "GET",
            "api/portfolio/diagnose",
            200,
            check_fields=["rows", "sector_breakdown", "current_buckets", "target_bands", "add_list", "trim_list"]
        )
        if success2:
            print(f"   Rows: {len(response2.get('rows', []))}")
            print(f"   Sector breakdown: {len(response2.get('sector_breakdown', []))} sectors")
            print(f"   Add list: {len(response2.get('add_list', []))} items")
            print(f"   Trim list: {len(response2.get('trim_list', []))} items")
        
        return success and success2, response2

    def test_portfolio_update(self):
        """U7: POST /api/portfolio/update"""
        # Test with empty update (should succeed but do nothing)
        success, response = self.run_test(
            "U7: Portfolio Update",
            "POST",
            "api/portfolio/update",
            200,
            data=[{"symbol": "NVDA", "shares": 100}],
            check_fields=["ok", "updated"]
        )
        if success:
            print(f"   Updated: {response.get('updated')} items")
        return success, response

    def test_reports(self):
        """U8: GET /api/reports/list and GET /api/reports/{date}"""
        success, response = self.run_test(
            "U8a: Reports List",
            "GET",
            "api/reports/list",
            200,
            check_fields=["reports"]
        )
        
        report_date = None
        if success:
            reports = response.get('reports', [])
            print(f"   Found {len(reports)} reports")
            if len(reports) > 0:
                report_date = reports[0].get('date')
                print(f"   Latest report date: {report_date}")
        
        # Test getting specific report
        if report_date:
            success2, response2 = self.run_test(
                "U8b: Get Report by Date",
                "GET",
                f"api/reports/{report_date}",
                200,
                check_fields=["date", "title", "markdown"]
            )
            if success2:
                print(f"   Report title: {response2.get('title')}")
                print(f"   Markdown length: {len(response2.get('markdown', ''))} chars")
        else:
            success2 = False
            print("⚠️  Skipping U8b: No reports available")
        
        return success and success2, response

    def test_report_download(self):
        """U9: GET /api/reports/{date}/download"""
        # First get a report date
        success, response = self.run_test(
            "U9: Report Download (get date first)",
            "GET",
            "api/reports/list",
            200
        )
        
        if success:
            reports = response.get('reports', [])
            if len(reports) > 0:
                report_date = reports[0].get('date')
                # Test download
                url = f"{self.base_url}/api/reports/{report_date}/download"
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200 and resp.headers.get('content-type') == 'text/plain; charset=utf-8':
                        self.tests_passed += 1
                        print(f"✅ Passed - Downloaded report for {report_date}")
                        print(f"   Content length: {len(resp.text)} chars")
                        return True, resp.text
                    else:
                        self.failed_tests.append("U9: Report Download")
                        print(f"❌ Failed - Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}")
                        return False, {}
                except Exception as e:
                    self.failed_tests.append("U9: Report Download")
                    print(f"❌ Failed - Error: {e}")
                    return False, {}
            else:
                print("⚠️  Skipping: No reports available")
                return False, {}
        return False, {}

    def test_settings_thresholds(self):
        """U10: GET and POST /api/settings/thresholds"""
        success, response = self.run_test(
            "U10a: Get Thresholds",
            "GET",
            "api/settings/thresholds",
            200
        )
        
        if success:
            print(f"   Thresholds keys: {list(response.keys())}")
            
            # Test update (round-trip)
            success2, response2 = self.run_test(
                "U10b: Update Thresholds",
                "POST",
                "api/settings/thresholds",
                200,
                data={"test_key": "test_value"},
                check_fields=["ok", "thresholds"]
            )
            return success and success2, response2
        return False, {}

    def test_settings_risk_profile(self):
        """U11: GET and POST /api/settings/risk-profile"""
        success, response = self.run_test(
            "U11a: Get Risk Profile",
            "GET",
            "api/settings/risk-profile",
            200,
            check_fields=["risk_profile", "options"]
        )
        
        if success:
            print(f"   Current risk profile: {response.get('risk_profile')}")
            print(f"   Available options: {response.get('options')}")
            
            # Test update (round-trip)
            current_profile = response.get('risk_profile')
            success2, response2 = self.run_test(
                "U11b: Update Risk Profile",
                "POST",
                "api/settings/risk-profile",
                200,
                data={"risk_profile": current_profile},
                check_fields=["ok", "risk_profile"]
            )
            return success and success2, response2
        return False, {}

    def test_fear_greed_history(self):
        """U12: GET /api/indicators/fear-greed"""
        success, response = self.run_test(
            "U12: Fear & Greed History",
            "GET",
            "api/indicators/fear-greed",
            200,
            params={"days": 60},
            check_fields=["history"]
        )
        if success:
            history = response.get('history', [])
            print(f"   Found {len(history)} history entries")
            if len(history) > 0:
                sample = history[-1]  # Latest
                print(f"   Latest: date={sample.get('date')}, global_fng={sample.get('global_fng')}, china_tech_fng={sample.get('china_tech_fng')}")
        return success, response

    def test_backtest(self):
        """U13: POST /api/backtest/run"""
        print("\n⏳ Note: Backtest may take a few seconds...")
        success, response = self.run_test(
            "U13: Backtest Run",
            "POST",
            "api/backtest/run",
            200,
            params={"symbol": "^IXIC", "days": 250},
            check_fields=["symbol", "buy_hold_return_pct", "strategy_return_pct", "curves"]
        )
        if success:
            print(f"   Symbol: {response.get('symbol')}")
            print(f"   Buy & Hold Return: {response.get('buy_hold_return_pct')}%")
            print(f"   Strategy Return: {response.get('strategy_return_pct')}%")
            print(f"   Buy & Hold MDD: {response.get('buy_hold_mdd_pct')}%")
            print(f"   Strategy MDD: {response.get('strategy_mdd_pct')}%")
        return success, response

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("🚀 Personal Investment Bank System - Backend API Testing")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Run all tests
        self.test_health()
        self.test_market_overview()
        self.test_sectors()
        self.test_watchlist()
        self.test_recommendations_today()
        self.test_portfolio()
        self.test_portfolio_update()
        self.test_reports()
        self.test_report_download()
        self.test_settings_thresholds()
        self.test_settings_risk_profile()
        self.test_fear_greed_history()
        self.test_backtest()

        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ Failed tests:")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        if self.critical_failures:
            print("\n🚨 Critical failures:")
            for failure in self.critical_failures:
                print(f"   - {failure}")
        
        print("=" * 80)
        
        return 0 if self.tests_passed == self.tests_run else 1


def main():
    tester = PIBAPITester()
    return tester.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
