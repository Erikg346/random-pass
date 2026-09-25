import React, { useState } from 'react';

export type GenerationEvent = {
    source: string;
    traceId: string | null;
    durationMs: number;
    length: number;
};

type PasswordGeneratorProps = {
    onGenerated?: (event: GenerationEvent) => void;
};

const PasswordGenerator: React.FC<PasswordGeneratorProps> = ({ onGenerated }) => {
    const [password, setPassword] = useState<string>('');
    const [length, setLength] = useState<number>(12);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [source, setSource] = useState<string | null>(null);
    const [copied, setCopied] = useState<boolean>(false);

    const generatePassword = async () => {
        const safeLength = Math.min(128, Math.max(8, length));
        setLength(safeLength);
        setLoading(true);
        setError(null);
        setCopied(false);
        try {
            const response = await fetch(`/generate-password?length=${safeLength}`);
            if (!response.ok) {
                throw new Error('Failed to generate password');
            }
            const data = await response.json();
            setPassword(data.password);
            setSource(data.source);
            onGenerated?.({
                source: data.source,
                traceId: data.trace_id,
                durationMs: data.duration_ms,
                length: safeLength,
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unable to reach the password API');
        } finally {
            setLoading(false);
        }
    };

    const copyPassword = async () => {
        await navigator.clipboard.writeText(password);
        setCopied(true);
    };

    return (
        <div className="generator-card">
            <div className="generator-heading">
                <div><p className="eyebrow">Request console</p><h3>Password generator</h3></div>
                {source && <span className="source-badge">{source === 'cache' ? 'Redis cache' : 'Fresh entropy'}</span>}
            </div>
            <div className="password-output" aria-live="polite">
                <span>{password || 'Your generated password will appear here'}</span>
                {password && <button className="copy-button" onClick={copyPassword} title="Copy password">{copied ? 'Copied' : 'Copy'}</button>}
            </div>
            <div className="generator-controls">
                <label htmlFor="password-length">Length <strong>{length}</strong></label>
                <input id="password-length" type="range" value={length} onChange={(e) => setLength(Number(e.target.value))} min="8" max="128" />
                <button className="generate-button" onClick={generatePassword} disabled={loading}>
                    {loading ? 'Tracing request...' : 'Generate password'} <span>→</span>
                </button>
            </div>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};

export default PasswordGenerator;