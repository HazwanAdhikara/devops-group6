import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

// Custom metrics tracking
const customLatencyTrend = new Trend('custom_latency_ms');
const errorRate = new Rate('error_rate');

// [LAMA - dinonaktifkan] BASE_URL lama hanya cocok kalau app berjalan di mesin yang sama dengan k6.
// const BASE_URL = 'http://localhost:3000';

// [BARU] BASE_URL bisa diatur dari command line.
// Default diarahkan ke public IP Application VM.
const BASE_URL = __ENV.BASE_URL || 'http://4.193.183.63:3000';

export const options = {
    // [LAMA - dinonaktifkan sementara] Skenario 1000 VUs terlalu berat untuk test awal dashboard.
    stages: [
        { duration: '1m', target: 500 },   // menit 1 naik ke 500 VUs
        { duration: '3m', target: 1000 },  // menit 2-4 tahan 1000 VUs
        { duration: '1m', target: 0 },     // menit 5 turun ke 0
    ],

    // [BARU] Skenario ringan dulu untuk memastikan grafik Grafana bergerak.
    // stages: [
    //    { duration: '30s', target: 10 },
    //    { duration: '1m', target: 30 },
    //    { duration: '30s', target: 0 },
    //],

    thresholds: {
        http_req_duration: ['p(95)<200'],
        error_rate: ['rate<0.05'],
    },
};

export default function () {
    // 1. Test Endpoint Users
    const resUsers = http.get(`${BASE_URL}/api/users`);

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

    sleep(1);
}
