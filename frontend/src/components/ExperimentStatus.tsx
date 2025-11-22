import React, { useEffect, useState } from 'react';
import { Activity, Clock, Loader } from 'lucide-react';
import { chaosLabAPI, type StatusResponse } from '../api/client';

interface ExperimentStatusProps {
    experimentId: string;
    onComplete: () => void;
}

export const ExperimentStatus: React.FC<ExperimentStatusProps> = ({
    experimentId,
    onComplete,
}) => {
    const [status, setStatus] = useState<StatusResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const pollStatus = async () => {
            try {
                const response = await chaosLabAPI.getStatus(experimentId);
                setStatus(response);

                if (response.status === 'completed') {
                    onComplete();
                } else if (response.status === 'failed') {
                    setError(response.message || 'Experiment failed');
                }
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to fetch status');
            }
        };

        // Poll every 2 seconds
        const interval = setInterval(pollStatus, 2000);
        pollStatus(); // Initial call

        return () => clearInterval(interval);
    }, [experimentId, onComplete]);

    if (error) {
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
                    <h3 style={{ color: 'var(--error)' }}>Experiment Failed</h3>
                    <p style={{ color: 'var(--text-muted)' }}>{error}</p>
                </div>
            </div>
        );
    }

    if (!status) {
        return (
            <div className="card fade-in">
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <Loader className="spinner" size={48} style={{ margin: '0 auto 1rem' }} />
                    <p>Loading experiment status...</p>
                </div>
            </div>
        );
    }

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'pending':
                return <span className="badge badge-info">Pending</span>;
            case 'running':
                return <span className="badge badge-warning">Running</span>;
            case 'analyzing':
                return <span className="badge badge-info">Analyzing</span>;
            case 'completed':
                return <span className="badge badge-success">Completed</span>;
            case 'failed':
                return <span className="badge badge-error">Failed</span>;
            default:
                return <span className="badge badge-info">{status}</span>;
        }
    };

    const getStatusMessage = (status: string) => {
        switch (status) {
            case 'pending':
                return 'Preparing experiment environment...';
            case 'running':
                return 'Running chaos scenario in E2B sandbox...';
            case 'analyzing':
                return 'Analyzing results with Groq AI...';
            case 'completed':
                return 'Experiment completed successfully!';
            case 'failed':
                return 'Experiment encountered an error';
            default:
                return 'Processing...';
        }
    };

    return (
        <div className="card fade-in">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <Activity size={32} color="#6366f1" />
                <div style={{ flex: 1 }}>
                    <h2 style={{ marginBottom: '0.5rem' }}>Experiment in Progress</h2>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Clock size={16} color="var(--text-muted)" />
                        <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            ID: {experimentId}
                        </span>
                    </div>
                </div>
                {getStatusBadge(status.status)}
            </div>

            {/* Progress Bar */}
            <div className="progress-bar">
                <div
                    className="progress-fill"
                    style={{
                        width: `${status.progress}%`,
                    }}
                />
            </div>

            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginTop: '0.5rem',
                }}
            >
                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    {getStatusMessage(status.status)}
                </span>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-primary)' }}>
                    {status.progress}%
                </span>
            </div>

            {/* Animated Status Indicator */}
            {status.status !== 'completed' && status.status !== 'failed' && (
                <div
                    style={{
                        marginTop: '1.5rem',
                        padding: '1rem',
                        background: 'var(--bg-tertiary)',
                        borderRadius: 'var(--radius-md)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                    }}
                >
                    <Loader className="spinner" size={24} />
                    <div>
                        <div style={{ fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-primary)' }}>
                            Please wait...
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            This may take a few minutes depending on the scenario
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
