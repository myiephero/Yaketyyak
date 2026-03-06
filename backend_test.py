#!/usr/bin/env python3
"""
Backend API Testing Suite for Terminal Translator
Tests all API endpoints for functionality and integration
"""

import requests
import json
import time
from datetime import datetime

class TerminalTranslatorTester:
    def __init__(self, base_url="https://cmd-simple.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            self.failed_tests.append({"name": name, "details": details, "response": response_data})
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
        print()

    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "knowledge_base_patterns", "ai_configured"]
                
                if all(field in data for field in expected_fields):
                    if data["status"] == "healthy" and data["knowledge_base_patterns"] > 0:
                        self.log_test(
                            "Health Check", 
                            True, 
                            f"Status: {data['status']}, KB patterns: {data['knowledge_base_patterns']}, AI configured: {data['ai_configured']}"
                        )
                    else:
                        self.log_test(
                            "Health Check", 
                            False, 
                            f"Unhealthy status or no KB patterns: {data}",
                            data
                        )
                else:
                    self.log_test(
                        "Health Check", 
                        False, 
                        f"Missing expected fields. Got: {list(data.keys())}",
                        data
                    )
            else:
                self.log_test(
                    "Health Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Health Check", False, f"Request failed: {str(e)}")

    def test_knowledge_base_stats(self):
        """Test /api/knowledge-base/stats endpoint"""
        try:
            response = requests.get(f"{self.api_base}/knowledge-base/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["total_patterns", "categories"]
                
                if all(field in data for field in expected_fields):
                    if data["total_patterns"] > 0 and isinstance(data["categories"], dict):
                        self.log_test(
                            "KB Stats", 
                            True, 
                            f"Total patterns: {data['total_patterns']}, Categories: {len(data['categories'])}"
                        )
                    else:
                        self.log_test(
                            "KB Stats", 
                            False, 
                            f"Invalid data structure: {data}",
                            data
                        )
                else:
                    self.log_test(
                        "KB Stats", 
                        False, 
                        f"Missing expected fields. Got: {list(data.keys())}",
                        data
                    )
            else:
                self.log_test(
                    "KB Stats", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("KB Stats", False, f"Request failed: {str(e)}")

    def test_translate_local_knowledge(self):
        """Test /api/translate with local knowledge base patterns"""
        test_cases = [
            {
                "text": "git commit -m 'test message'",
                "mode": "beginner",
                "expected_source": "local"
            },
            {
                "text": "npm install",
                "mode": "familiar", 
                "expected_source": "local"
            },
            {
                "text": "permission denied",
                "mode": "beginner",
                "expected_source": "local"
            }
        ]

        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_base}/translate",
                    json={"text": case["text"], "mode": case["mode"]},
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    expected_fields = ["explanation", "source"]
                    
                    if all(field in data for field in expected_fields):
                        if data["source"] == case["expected_source"] and data["explanation"]:
                            lookup_time = data.get("lookup_time_ms", "N/A")
                            self.log_test(
                                f"Translate Local ({case['mode']}: '{case['text'][:30]}...')",
                                True,
                                f"Source: {data['source']}, Lookup: {lookup_time}ms, Pattern: {data.get('matched_pattern', 'N/A')}"
                            )
                        else:
                            self.log_test(
                                f"Translate Local ({case['mode']}: '{case['text'][:30]}...')",
                                False,
                                f"Expected local source but got: {data['source']}",
                                data
                            )
                    else:
                        self.log_test(
                            f"Translate Local ({case['mode']}: '{case['text'][:30]}...')",
                            False,
                            f"Missing expected fields. Got: {list(data.keys())}",
                            data
                        )
                else:
                    self.log_test(
                        f"Translate Local ({case['mode']}: '{case['text'][:30]}...')",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_test(
                    f"Translate Local ({case['mode']}: '{case['text'][:30]}...')",
                    False,
                    f"Request failed: {str(e)}"
                )

    def test_translate_ai_fallback(self):
        """Test /api/translate with AI fallback for unknown patterns"""
        test_cases = [
            {
                "text": "some_very_unique_command_that_should_not_exist_in_kb_12345",
                "mode": "beginner",
                "expected_source": "ai"
            },
            {
                "text": "ExtremelySpecificErrorThatDoesNotExistAnywhere98765",
                "mode": "familiar",
                "expected_source": "ai"
            }
        ]

        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_base}/translate",
                    json={"text": case["text"], "mode": case["mode"]},
                    headers={"Content-Type": "application/json"},
                    timeout=30  # AI calls may take longer
                )
                
                if response.status_code == 200:
                    data = response.json()
                    expected_fields = ["explanation", "source"]
                    
                    if all(field in data for field in expected_fields):
                        if data["source"] in ["ai", "error"] and data["explanation"]:
                            self.log_test(
                                f"Translate AI Fallback ({case['mode']}: '{case['text'][:30]}...')",
                                True,
                                f"Source: {data['source']}, Model: {data.get('model', 'N/A')}"
                            )
                        else:
                            self.log_test(
                                f"Translate AI Fallback ({case['mode']}: '{case['text'][:30]}...')",
                                False,
                                f"Expected AI/error source but got: {data['source']}",
                                data
                            )
                    else:
                        self.log_test(
                            f"Translate AI Fallback ({case['mode']}: '{case['text'][:30]}...')",
                            False,
                            f"Missing expected fields. Got: {list(data.keys())}",
                            data
                        )
                else:
                    self.log_test(
                        f"Translate AI Fallback ({case['mode']}: '{case['text'][:30]}...')",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_test(
                    f"Translate AI Fallback ({case['mode']}: '{case['text'][:30]}...')",
                    False,
                    f"Request failed: {str(e)}"
                )

    def test_github_analyzer(self):
        """Test /api/github/analyze endpoint"""
        test_cases = [
            {
                "url": "https://github.com/torvalds/linux",
                "mode": "beginner"
            },
            {
                "url": "facebook/react",
                "mode": "familiar"
            },
            {
                "url": "https://github.com/nonexistent-user/nonexistent-repo-12345",
                "mode": "beginner",
                "should_fail": True
            }
        ]

        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_base}/github/analyze",
                    json={"url": case["url"], "mode": case["mode"]},
                    headers={"Content-Type": "application/json"},
                    timeout=30  # GitHub API calls may take time
                )
                
                should_fail = case.get("should_fail", False)
                
                if should_fail:
                    # Expect failure for nonexistent repo
                    if response.status_code == 400:
                        self.log_test(
                            f"GitHub Analyze (Error case: '{case['url']}')",
                            True,
                            f"Correctly failed with HTTP 400: {response.json().get('detail', 'Unknown error')}"
                        )
                    else:
                        self.log_test(
                            f"GitHub Analyze (Error case: '{case['url']}')",
                            False,
                            f"Expected HTTP 400 but got {response.status_code}: {response.text}"
                        )
                else:
                    # Expect success for valid repos
                    if response.status_code == 200:
                        data = response.json()
                        expected_fields = ["repo", "stats", "meta", "assessment", "summary"]
                        
                        if all(field in data for field in expected_fields):
                            repo_data = data["repo"]
                            stats_data = data["stats"]
                            
                            if repo_data.get("name") and stats_data.get("stars") is not None:
                                self.log_test(
                                    f"GitHub Analyze ({case['mode']}: '{case['url']}')",
                                    True,
                                    f"Repo: {repo_data['name']}, Stars: {stats_data['stars']}, Assessment: {data['assessment'].get('tier_label', 'N/A')}"
                                )
                            else:
                                self.log_test(
                                    f"GitHub Analyze ({case['mode']}: '{case['url']}')",
                                    False,
                                    f"Missing repo name or stats data",
                                    data
                                )
                        else:
                            self.log_test(
                                f"GitHub Analyze ({case['mode']}: '{case['url']}')",
                                False,
                                f"Missing expected fields. Got: {list(data.keys())}",
                                data
                            )
                    else:
                        self.log_test(
                            f"GitHub Analyze ({case['mode']}: '{case['url']}')",
                            False,
                            f"HTTP {response.status_code}: {response.text}"
                        )
                    
            except requests.exceptions.RequestException as e:
                self.log_test(
                    f"GitHub Analyze ({case['mode']}: '{case['url']}')",
                    False,
                    f"Request failed: {str(e)}"
                )

    def test_input_validation(self):
        """Test input validation for API endpoints"""
        
        # Test empty translate request
        try:
            response = requests.post(
                f"{self.api_base}/translate",
                json={"text": "", "mode": "beginner"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error expected
                self.log_test("Input Validation (Empty text)", True, f"Correctly rejected empty input: HTTP 422")
            else:
                self.log_test("Input Validation (Empty text)", False, f"Expected HTTP 422 but got {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Input Validation (Empty text)", False, f"Request failed: {str(e)}")

        # Test invalid mode
        try:
            response = requests.post(
                f"{self.api_base}/translate",
                json={"text": "test command", "mode": "invalid_mode"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error expected
                self.log_test("Input Validation (Invalid mode)", True, f"Correctly rejected invalid mode: HTTP 422")
            else:
                self.log_test("Input Validation (Invalid mode)", False, f"Expected HTTP 422 but got {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Input Validation (Invalid mode)", False, f"Request failed: {str(e)}")

    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🚀 Starting Terminal Translator Backend API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_health_endpoint()
        self.test_knowledge_base_stats()
        self.test_translate_local_knowledge()
        self.test_translate_ai_fallback()
        self.test_github_analyzer()
        self.test_input_validation()
        
        end_time = time.time()
        
        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print(f"⏱️  Total time: {end_time - start_time:.2f}s")
        print(f"✅ Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Failed: {len(self.failed_tests)}/{self.tests_run}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   - {test['name']}: {test['details']}")
        
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "failed_tests": self.failed_tests,
            "success_rate": (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0
        }

if __name__ == "__main__":
    tester = TerminalTranslatorTester()
    result = tester.run_all_tests()
    
    # Exit with error code if tests failed
    exit(0 if len(result["failed_tests"]) == 0 else 1)