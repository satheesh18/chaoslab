import React, { useEffect, useState } from 'react';
import { CheckCircle, AlertTriangle, TrendingUp, BarChart3, ExternalLink } from 'lucide-react';
import { chaosLabAPI, type ResultsResponse } from '../api/client';

interface ResultsViewProps {
    experimentId: string;
    onNewExperiment: () => void;
}

export const ResultsView: React.FC<ResultsViewProps> = ({ experimentId, onNewExperiment }) => {
    const [results, setResults] = useState<ResultsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchResults = async () => {
            try {
                const response = await chaosLabAPI.getResults(experimentId);
                setResults(response);
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to fetch results');
            } finally {
                setLoading(false);
            }
        };

        fetchResults();
    }, [experimentId]);

    if (loading) {
        return (
            <div className="card fade-in">
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <div className="spinner" style={{ margin: '0 auto 1rem' }} />
                    <p>Loading results...</p>
                </div>
            </div>
        );
    }

    if (error || !results) {
        return (
            <div className="card fade-in">
                <div
                    style={{
                        padding: '2rem',
                        textAlign: 'center',
                        background: 'rgba(239, 68, 68, 0.1)',
                        borderRadius: 'var(--radius-lg)',
                    }}
                >
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>
                    <h3 style={{ color: 'var(--error)' }}>Failed to Load Results</h3>
                    <p style={{ color: 'var(--text-muted)' }}>{error}</p>
                </div>
            </div>
        );
    }

    const getSeverityBadge = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'low':
                return <span className="badge badge-success">Low Severity</span>;
            case 'medium':
                return <span className="badge badge-warning">Medium Severity</span>;
            case 'high':
                return <span className="badge badge-error">High Severity</span>;
            default:
                return <span className="badge badge-info">{severity}</span>;
        }
    };

    return (
        <div className="fade-in">
            {/* Header */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <CheckCircle size={32} color="#10b981" />
                        <div>
                            <h2 style={{ marginBottom: '0.5rem' }}>Experiment Complete</h2>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                ID: {experimentId}
                            </div>
                        </div>
                    </div>
                    {getSeverityBadge(results.severity)}
                </div>
            </div>

            {/* AI Summary */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                    <TrendingUp size={24} color="#6366f1" />
                    <h3 style={{ marginBottom: 0 }}>AI Analysis Summary</h3>
                </div>
                <p style={{ fontSize: '1.125rem', lineHeight: 1.8, color: 'var(--text-primary)' }}>
                    {results.summary}
                </p>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-4" style={{ marginBottom: '2rem' }}>
                <div className="metric-card">
                    <div className="metric-value">{results.metrics.cpu_peak.toFixed(1)}%</div>
                    <div className="metric-label">Peak CPU</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">{results.metrics.memory_peak.toFixed(1)}%</div>
                    <div className="metric-label">Peak Memory</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">{results.metrics.error_count}</div>
                    <div className="metric-label">Errors</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">
                        {results.metrics.recovery_time_seconds 
                            ? results.metrics.recovery_time_seconds.toFixed(1) 
                            : 'N/A'}
                        {results.metrics.recovery_time_seconds && 's'}
                    </div>
                    <div className="metric-label">Recovery Time</div>
                </div>
            </div>

            {/* Recommendations */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                    <AlertTriangle size={24} color="#f59e0b" />
                    <h3 style={{ marginBottom: 0 }}>Recommendations</h3>
                </div>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                    {results.recommendations.map((rec, index) => (
                        <li
                            key={index}
                            style={{
                                padding: '1rem',
                                background: 'var(--bg-tertiary)',
                                borderRadius: 'var(--radius-md)',
                                marginBottom: '0.75rem',
                                borderLeft: '4px solid var(--accent-primary)',
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'start', gap: '0.75rem' }}>
                                <span style={{ fontSize: '1.25rem' }}>💡</span>
                                <span style={{ color: 'var(--text-primary)' }}>{rec}</span>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>

            {/* Grafana Dashboard */}
            {results.grafana_url && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <div
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            marginBottom: '1rem',
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <BarChart3 size={24} color="#6366f1" />
                            <h3 style={{ marginBottom: 0 }}>Grafana Dashboard</h3>
                        </div>
                        <a
                            href={results.grafana_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-secondary"
                            style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}
                        >
                            <ExternalLink size={16} />
                            Open in New Tab
                        </a>
                    </div>
                    <div className="iframe-container">
                        <iframe src={results.grafana_url} title="Grafana Dashboard" />
                    </div>
                </div>
            )}

            {/* Actions */}
            <div style={{ textAlign: 'center' }}>
                <button
                    onClick={onNewExperiment}
                    className="btn btn-primary"
                    style={{ padding: '1rem 2rem', fontSize: '1.125rem' }}
                >
                    Run Another Experiment
                </button>
            </div>
        </div>
    );
};
