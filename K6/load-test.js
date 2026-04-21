import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

// Custom metrics tracking
const customLatencyTrend = new Trend('custom_latency_ms');
const errorRate = new Rate('error_rate');

export const options = {
    // Skenario 1000 VUs selama 5 menit dengan ramping up
    stages:[
        { duration: '1m', target: 500 },  // Menit 1: Naik bertahap ke 500 VUs
        { duration: '3m', target: 1000 }, // Menit 2-4: Tahan di 1000 VUs
        { duration: '1m', target: 0 },    // Menit 5: Turun bertahap ke 0
    ],
    // Threshold: p95 latency < 200ms
    thresholds: {
        http_req_duration: ['p(95)<200'], 
        error_rate: ['rate<0.05'], // Toleransi error maksimal 5%
    },
};

export default function () {
    const BASE_URL = 'http://localhost:3000';

    // 1. Test Endpoint Users
    const resUsers = http.get(`${BASE_URL}/api/users`);
    
    // Validasi dan custom metrics
    const checkUser = check(resUsers, {
        'Users status is 200': (r) => r.status === 200,
    });
    
    errorRate.add(!checkUser);
    customLatencyTrend.add(resUsers.timings.duration);

    // 2. Test Endpoint Products
    const resProducts = http.get(`${BASE_URL}/api/products`);
    
    const checkProduct = check(resProducts, {
        'Products status is 200': (r) => r.status === 200,
    });
    
    errorRate.add(!checkProduct);
    customLatencyTrend.add(resProducts.timings.duration);

    // Jeda antar request (simulasi user nyata)
    sleep(1);
}