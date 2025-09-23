import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp-up to 10 users
    { duration: '1m', target: 10 },    // Hold at 10 users
    { duration: '30s', target: 20 },   // Ramp-up to 20 users
    { duration: '1m', target: 20 },    // Hold at 20 users
    { duration: '30s', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    errors: ['rate<0.1'],             // Error rate must be less than 10%
  },
};

const BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000';

export default function () {
  // Health check endpoint
  let response = http.get(`${BASE_URL}/health`);
  check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  }) || errorRate.add(1);

  sleep(1);

  // API docs endpoint
  response = http.get(`${BASE_URL}/docs`);
  check(response, {
    'docs status is 200': (r) => r.status === 200,
    'docs response time < 500ms': (r) => r.timings.duration < 500,
  }) || errorRate.add(1);

  sleep(1);

  // Version endpoint
  response = http.get(`${BASE_URL}/api/v1/version`);
  check(response, {
    'version status is 200': (r) => r.status === 200,
    'version response time < 100ms': (r) => r.timings.duration < 100,
  }) || errorRate.add(1);

  sleep(2);

  // Authentication endpoint (if it exists)
  const authPayload = JSON.stringify({
    username: 'test_user',
    password: 'test_password',
  });
  
  const authParams = {
    headers: { 'Content-Type': 'application/json' },
  };
  
  response = http.post(`${BASE_URL}/api/v1/auth/token`, authPayload, authParams);
  check(response, {
    'auth response is valid': (r) => r.status === 200 || r.status === 401,
    'auth response time < 300ms': (r) => r.timings.duration < 300,
  }) || errorRate.add(1);

  sleep(1);
}