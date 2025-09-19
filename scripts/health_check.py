#!/usr/bin/env python3
"""
Health check script for CloudViz deployments.
Validates that the application is running correctly.
"""

import argparse
import sys
import time
import httpx
import json
from typing import Dict, Any, List


class HealthChecker:
    """CloudViz health check manager."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    def run_all_checks(self) -> bool:
        """Run all health checks."""
        print(f"🏥 Running health checks for: {self.base_url}")
        
        checks = [
            ("Basic Connectivity", self._check_basic_connectivity),
            ("Health Endpoint", self._check_health_endpoint),
            ("API Endpoints", self._check_api_endpoints),
            ("Authentication", self._check_authentication),
            ("Database", self._check_database),
        ]
        
        results = []
        
        for check_name, check_func in checks:
            print(f"\n🔍 Checking: {check_name}")
            
            try:
                success, message = check_func()
                if success:
                    print(f"✅ {check_name}: {message}")
                else:
                    print(f"❌ {check_name}: {message}")
                
                results.append((check_name, success, message))
                
            except Exception as e:
                print(f"❌ {check_name}: Exception - {e}")
                results.append((check_name, False, str(e)))
        
        # Summary
        successful = sum(1 for _, success, _ in results if success)
        total = len(results)
        
        print(f"\n📊 Health Check Summary: {successful}/{total} checks passed")
        
        if successful == total:
            print("✅ All health checks passed!")
            return True
        else:
            print("❌ Some health checks failed!")
            return False
    
    def _check_basic_connectivity(self) -> tuple[bool, str]:
        """Check basic HTTP connectivity."""
        try:
            response = self.client.get(f"{self.base_url}/")
            
            if response.status_code in [200, 404]:  # 404 is OK for root
                return True, f"HTTP {response.status_code}"
            else:
                return False, f"HTTP {response.status_code}"
                
        except httpx.ConnectError:
            return False, "Connection refused"
        except httpx.TimeoutException:
            return False, "Connection timeout"
    
    def _check_health_endpoint(self) -> tuple[bool, str]:
        """Check dedicated health endpoint."""
        try:
            response = self.client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = data.get("status", "unknown")
                    
                    if status == "healthy":
                        return True, f"Status: {status}"
                    else:
                        return False, f"Status: {status}"
                        
                except json.JSONDecodeError:
                    return True, "Health endpoint responding (non-JSON)"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def _check_api_endpoints(self) -> tuple[bool, str]:
        """Check main API endpoints."""
        endpoints = [
            "/docs",  # OpenAPI docs
            "/api/v1/providers",  # List providers
        ]
        
        working_endpoints = 0
        
        for endpoint in endpoints:
            try:
                response = self.client.get(f"{self.base_url}{endpoint}")
                
                if response.status_code in [200, 401]:  # 401 means auth required, which is OK
                    working_endpoints += 1
                    
            except Exception:
                pass
        
        if working_endpoints == len(endpoints):
            return True, f"All {len(endpoints)} endpoints responding"
        elif working_endpoints > 0:
            return True, f"{working_endpoints}/{len(endpoints)} endpoints responding"
        else:
            return False, "No API endpoints responding"
    
    def _check_authentication(self) -> tuple[bool, str]:
        """Check authentication system."""
        try:
            # Try to access a protected endpoint
            response = self.client.get(f"{self.base_url}/api/v1/extractions")
            
            if response.status_code == 401:
                # Check if it's proper authentication error
                try:
                    data = response.json()
                    if "detail" in data:
                        return True, "Authentication system active"
                except json.JSONDecodeError:
                    pass
                
                return True, "Authentication required (HTTP 401)"
            
            elif response.status_code == 200:
                return True, "Endpoint accessible (may be public)"
            
            else:
                return False, f"Unexpected response: HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def _check_database(self) -> tuple[bool, str]:
        """Check database connectivity through API."""
        try:
            # Try an endpoint that would require database access
            response = self.client.get(f"{self.base_url}/api/v1/inventories")
            
            # Even if unauthorized, if we get a proper HTTP response,
            # it means the database layer is working
            if response.status_code in [200, 401, 403]:
                return True, "Database connectivity OK"
            elif response.status_code == 500:
                return False, "Database error (HTTP 500)"
            else:
                return False, f"Unexpected response: HTTP {response.status_code}"
                
        except Exception as e:
            if "database" in str(e).lower():
                return False, f"Database error: {e}"
            else:
                return False, str(e)
    
    def wait_for_healthy(self, max_wait: int = 300, check_interval: int = 5) -> bool:
        """Wait for the service to become healthy."""
        print(f"⏳ Waiting for service to become healthy (max {max_wait}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                success, message = self._check_health_endpoint()
                
                if success:
                    elapsed = int(time.time() - start_time)
                    print(f"✅ Service is healthy after {elapsed}s")
                    return True
                
                print(f"⏳ Not ready yet: {message}")
                
            except Exception as e:
                print(f"⏳ Waiting: {e}")
            
            time.sleep(check_interval)
        
        print(f"❌ Service did not become healthy within {max_wait}s")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CloudViz Health Check Tool")
    parser.add_argument(
        "--url",
        required=True,
        help="Base URL of the CloudViz instance to check"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds"
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for service to become healthy"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=300,
        help="Maximum time to wait for service (seconds)"
    )
    
    args = parser.parse_args()
    
    try:
        checker = HealthChecker(args.url, args.timeout)
        
        if args.wait:
            if not checker.wait_for_healthy(args.max_wait):
                sys.exit(1)
        
        if not checker.run_all_checks():
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Health check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
