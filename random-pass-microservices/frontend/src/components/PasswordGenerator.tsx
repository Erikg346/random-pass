import React, { useState } from 'react';

const PasswordGenerator: React.FC = () => {
    const [password, setPassword] = useState<string>('');
    const [length, setLength] = useState<number>(12);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const generatePassword = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`/generate-password?length=${length}`);
            if (!response.ok) {
                throw new Error('Failed to generate password');
            }
            const data = await response.json();
            setPassword(data.password);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h2>Password Generator</h2>
            <label>
                Length:
                <input
                    type="number"
                    value={length}
                    onChange={(e) => setLength(Number(e.target.value))}
                    min="1"
                />
            </label>
            <button onClick={generatePassword} disabled={loading}>
                {loading ? 'Generating...' : 'Generate Password'}
            </button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {password && (
                <div>
                    <h3>Generated Password:</h3>
                    <p>{password}</p>
                </div>
            )}
        </div>
    );
};

export default PasswordGenerator;