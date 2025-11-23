import React, { useEffect, useState } from 'react';
import { AlertTriangle, TrendingUp, ExternalLink } from 'lucide-react';
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Experiment Results</h2>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginTop: '4px' }}>
                        <span className="text-sm text-muted font-mono">{experimentId}</span>
                        <span className="badge badge-neutral">Completed</span>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button onClick={onNewExperiment} className="btn btn-secondary">
                        New Experiment
                    </button>
                    {results.grafana_url && (
                        <a href={results.grafana_url} target="_blank" rel="noopener noreferrer" className="btn btn-primary" style={{ textDecoration: 'none' }}>
                            Open Grafana <ExternalLink size={14} />
                        </a>
                    )}
                </div>
            </div>

            {/* Metrics Row */}
            <div className="grid-cols-4" style={{ marginBottom: '24px' }}>
                <div className="panel" style={{ padding: '20px' }}>
                    <div className="text-xs text-muted" style={{ marginBottom: '8px' }}>Peak CPU</div>
                    <div className="text-xl font-mono" style={{ fontSize: '24px', fontWeight: 600 }}>{results.metrics.cpu_peak.toFixed(1)}%</div>
                    <div style={{ height: '4px', background: 'var(--bg-subtle)', marginTop: '12px', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${results.metrics.cpu_peak}%`, background: 'var(--text-primary)' }} />
                    </div>
                </div>
                <div className="panel" style={{ padding: '20px' }}>
                    <div className="text-xs text-muted" style={{ marginBottom: '8px' }}>Peak Memory</div>
                    <div className="text-xl font-mono" style={{ fontSize: '24px', fontWeight: 600 }}>{results.metrics.memory_peak.toFixed(1)}%</div>
                    <div style={{ height: '4px', background: 'var(--bg-subtle)', marginTop: '12px', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${results.metrics.memory_peak}%`, background: 'var(--text-primary)' }} />
                    </div>
                </div>
                <div className="panel" style={{ padding: '20px' }}>
                    <div className="text-xs text-muted" style={{ marginBottom: '8px' }}>Errors</div>
                    <div className="text-xl font-mono" style={{ fontSize: '24px', fontWeight: 600, color: results.metrics.error_count > 0 ? 'var(--error)' : 'var(--text-primary)' }}>
                        {results.metrics.error_count}
                    </div>
                    <div className="text-xs text-muted" style={{ marginTop: '8px' }}>
                        {results.metrics.error_count === 0 ? 'No errors detected' : 'Exceptions caught'}
                    </div>
                </div>
                <div className="panel" style={{ padding: '20px' }}>
                    <div className="text-xs text-muted" style={{ marginBottom: '8px' }}>Recovery Time</div>
                    <div className="text-xl font-mono" style={{ fontSize: '24px', fontWeight: 600 }}>{results.metrics.recovery_time_seconds.toFixed(1)}s</div>
                    <div className="text-xs text-muted" style={{ marginTop: '8px' }}>Time to stabilize</div>
                </div>
            </div>

            {/* Analysis & Recommendations */}
            <div className="grid-cols-2" style={{ marginBottom: '24px' }}>
                <div className="panel" style={{ padding: '24px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                        <TrendingUp size={16} />
                        <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>AI Analysis</h3>
                    </div>
                    <p style={{ fontSize: '14px', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                        {results.summary}
                    </p>
                </div>

                <div className="panel" style={{ padding: '24px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                        <AlertTriangle size={16} />
                        <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>Recommendations</h3>
                    </div>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                        {results.recommendations.map((rec, index) => (
                            <li key={index} style={{ 
                                padding: '12px', 
                                background: 'var(--bg-subtle)', 
                                borderRadius: 'var(--radius-sm)', 
                                marginBottom: '8px',
                                fontSize: '13px',
                                borderLeft: '2px solid var(--warning)'
                            }}>
                                {rec}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Grafana Embed */}
            {results.grafana_url && (
                <div className="panel" style={{ padding: '4px', height: '500px', overflow: 'hidden' }}>
                    <iframe 
                        src={results.grafana_url.replace('/d/', '/d-solo/')} 
                        width="100%" 
                        height="100%" 
                        frameBorder="0"
                        style={{ borderRadius: 'var(--radius-sm)', background: 'var(--bg-surface)' }}
                    ></iframe>
                </div>
            )}
        </div>
    );
};
