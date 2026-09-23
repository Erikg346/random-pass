import React from 'react';
import PasswordGenerator from './components/PasswordGenerator';
import './styles.css';

const App: React.FC = () => {
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
                        OpenTelemetry Collector, and Jaeger.
                    </p>
                    <PasswordGenerator />
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
                        <div className="service-row"><span className="service-icon api">API</span><span><strong>Password API</strong><small>Flask · port 5000</small></span><b>UP</b></div>
                        <div className="service-row"><span className="service-icon data">DB</span><span><strong>Redis cache</strong><small>60 second response cache</small></span><b>UP</b></div>
                        <div className="service-row"><span className="service-icon trace">OT</span><span><strong>Trace pipeline</strong><small>OTLP → Collector → Jaeger</small></span><b>UP</b></div>
                    </div>
                    <div className="panel-links">
                        <a href="http://localhost:16686" target="_blank" rel="noreferrer">Open Jaeger traces <span>↗</span></a>
                        <a href="http://localhost:4000/feature/" target="_blank" rel="noreferrer">Open flag configurator <span>↗</span></a>
                    </div>
                </aside>
            </section>

            <footer className="footer-note">OpenTelemetry is on the path of every generation request.</footer>
        </main>
    );
};

export default App;