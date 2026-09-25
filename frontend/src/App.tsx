import React, { useEffect, useState } from 'react';
import PasswordGenerator, { GenerationEvent } from './components/PasswordGenerator';
import './styles.css';

type HealthState = {
    status: string;
    services?: { password_api: string; redis: string; policy_service?: string; notification_service?: string };
};

type MetricsState = {
    requests: number;
    cache_hit_rate: number;
    uptime_seconds: number;
};

const App: React.FC = () => {
    const [health, setHealth] = useState<HealthState>({ status: 'CHECKING' });
    const [metrics, setMetrics] = useState<MetricsState>({ requests: 0, cache_hit_rate: 0, uptime_seconds: 0 });
    const [activity, setActivity] = useState<GenerationEvent[]>([]);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const [healthResponse, metricsResponse, policyResponse] = await Promise.all([
                    fetch('/health'), fetch('/metrics'), fetch('/policy-health')
                ]);
                const apiHealth = await healthResponse.json();
                const policyHealth = await policyResponse.json();
                setHealth({
                    ...apiHealth,
                    services: {
                        ...apiHealth.services,
                        policy_service: policyHealth.status,
                    },
                });
                setMetrics(await metricsResponse.json());
            } catch {
                setHealth({ status: 'DOWN' });
            }
        };

        checkHealth();
        const interval = window.setInterval(checkHealth, 10000);
        return () => window.clearInterval(interval);
    }, []);

    const recordGeneration = (event: GenerationEvent) => {
        setActivity((current) => [event, ...current].slice(0, 4));
    };

    const apiStatus = health.services?.password_api || health.status;
    const redisStatus = health.services?.redis || 'CHECKING';
    const policyStatus = health.services?.policy_service || 'CHECKING';
    const notificationStatus = health.services?.notification_service || 'CHECKING';

    return (
        <main className="app-shell">
            <header className="topbar">
                <div className="brand-mark">R/P</div>
                <div>
                    <p className="eyebrow">Random Pass / Operations</p>
                    <h1>Generate securely. See everything.</h1>
                </div>
                <span className="live-pill"><span /> Live stack</span>
            </header>

            <section className="hero-grid">
                <div className="hero-copy">
                    <p className="eyebrow accent">Instrumented password service</p>
                    <h2>A better password, with a clearer signal.</h2>
                    <p className="hero-description">
                        Generate a password and follow the request through the API, Redis,
                        OpenTelemetry Collector, and Elastic.
                    </p>
                    <PasswordGenerator onGenerated={recordGeneration} />
                </div>

                <aside className="observability-panel">
                    <div className="panel-heading">
                        <div>
                            <p className="eyebrow">System view</p>
                            <h2>Service signals</h2>
                        </div>
                        <span className="signal-dot" />
                    </div>
                    <div className="service-list">
                        <div className="service-row"><span className="service-icon api">API</span><span><strong>Password API</strong><small>Flask · port 5000</small></span><b className={apiStatus !== 'UP' ? 'status-warn' : ''}>{apiStatus}</b></div>
                        <div className="service-row"><span className="service-icon data">DB</span><span><strong>Redis cache</strong><small>60 second response cache</small></span><b className={redisStatus !== 'UP' ? 'status-warn' : ''}>{redisStatus}</b></div>
                        <div className="service-row"><span className="service-icon trace">PL</span><span><strong>Policy service</strong><small>Rules · port 5001</small></span><b className={policyStatus !== 'UP' ? 'status-warn' : ''}>{policyStatus}</b></div>
                        <div className="service-row"><span className="service-icon trace">NO</span><span><strong>Notification service</strong><small>Events · port 5003</small></span><b className={notificationStatus !== 'UP' ? 'status-warn' : ''}>{notificationStatus}</b></div>
                        <div className="service-row"><span className="service-icon trace">OT</span><span><strong>Trace pipeline</strong><small>OTLP → Collector → Elastic</small></span><b>UP</b></div>
                    </div>
                    <div className="panel-links">
                        <a href="http://localhost:5601/app/apm/services" target="_blank" rel="noreferrer">Open Elastic traces <span>↗</span></a>
                        <a href="http://localhost:4000/" target="_blank" rel="noreferrer">Open flag configurator <span>↗</span></a>
                    </div>
                    <div className="activity-feed">
                        <div className="activity-heading"><p className="eyebrow">Recent activity</p><span>{activity.length} requests</span></div>
                        {activity.length === 0 ? <p className="empty-activity">Generate a password to populate the trace feed.</p> : activity.map((event, index) => (
                            <div className="activity-row" key={`${event.traceId}-${index}`}>
                                <span className="activity-dot" />
                                <span><strong>{event.source === 'cache' ? 'Cache hit' : 'Fresh generation'}</strong><small>{event.length} chars · {event.durationMs}ms</small></span>
                                {event.traceId && <a href="http://localhost:5601/app/apm/services" target="_blank" rel="noreferrer">Trace ↗</a>}
                            </div>
                        ))}
                    </div>
                </aside>
            </section>

            <section className="metrics-strip" aria-label="Service metrics">
                <div><span>Requests</span><strong>{metrics.requests}</strong></div>
                <div><span>Cache hit rate</span><strong>{metrics.cache_hit_rate}%</strong></div>
                <div><span>API uptime</span><strong>{Math.floor(metrics.uptime_seconds / 60)}m {metrics.uptime_seconds % 60}s</strong></div>
                <div><span>Telemetry</span><strong className="metrics-live"><i /> Streaming</strong></div>
            </section>

            <footer className="footer-note">OpenTelemetry is on the path of every generation request.</footer>
        </main>
    );
};

export default App;