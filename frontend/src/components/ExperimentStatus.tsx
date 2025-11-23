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

    const getStepLabel = (step: string) => {
        switch (step) {
            case 'pending': return 'Setup';
            case 'running': return 'Chaos';
            case 'analyzing': return 'Analysis';
            case 'completed': return 'Done';
            default: return step;
        }
    };

    return (
        <div className="panel fade-in" style={{ padding: '48px', textAlign: 'center', maxWidth: '700px', margin: '0 auto' }}>
            <div style={{ marginBottom: '24px' }}>
                <Activity size={48} style={{ margin: '0 auto', color: 'var(--text-primary)' }} />
            </div>

            <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>Experiment in Progress</h2>
            <p className="text-muted" style={{ marginBottom: '8px', fontSize: '14px' }}>
                Running chaos scenario
            </p>
            <p className="font-mono text-primary" style={{ marginBottom: '32px', fontSize: '13px' }}>
                {experimentId}
            </p>

            {/* Status Badge */}
            <div style={{ marginBottom: '24px' }}>
                {getStatusBadge(status.status)}
            </div>

            {/* Progress Bar */}
            <div style={{ marginBottom: '32px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', fontSize: '14px' }}>
                    <span style={{ fontWeight: 500, color: 'var(--text-secondary)' }}>{getStatusMessage(status.status)}</span>
                    <span className="font-mono" style={{ fontWeight: 600 }}>{status.progress}%</span>
                </div>
                
                <div style={{ height: '8px', background: 'var(--bg-subtle)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div
                        style={{
                            height: '100%',
                            width: `${status.progress}%`,
                            background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))',
                            transition: 'width 0.5s ease',
                            borderRadius: '4px'
                        }}
                    />
                </div>
            </div>

            {/* Steps Visualization */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', alignItems: 'center' }}>
                {['pending', 'running', 'analyzing', 'completed'].map((step, index) => {
                    const steps = ['pending', 'running', 'analyzing', 'completed'];
                    const currentIdx = steps.indexOf(status.status);
                    const stepIdx = steps.indexOf(step);
                    const isActive = stepIdx <= currentIdx;
                    const isCurrent = stepIdx === currentIdx;
                    
                    return (
                        <div key={step} style={{ display: 'flex', alignItems: 'center', flexDirection: 'column', gap: '8px' }}>
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                <div style={{ 
                                    width: isCurrent ? '12px' : '8px', 
                                    height: isCurrent ? '12px' : '8px', 
                                    borderRadius: '50%', 
                                    background: isActive ? 'var(--text-primary)' : 'var(--bg-subtle)',
                                    transition: 'all 0.3s ease',
                                    border: isCurrent ? '2px solid var(--accent-primary)' : 'none'
                                }} />
                                {index < 3 && (
                                    <div style={{ 
                                        width: '48px', 
                                        height: '2px', 
                                        background: isActive ? 'var(--text-primary)' : 'var(--bg-subtle)', 
                                        margin: '0 8px',
                                        transition: 'all 0.3s ease'
                                    }} />
                                )}
                            </div>
                            <div style={{ 
                                fontSize: '11px', 
                                color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                                fontWeight: isCurrent ? 600 : 400,
                                transition: 'all 0.3s ease'
                            }}>
                                {getStepLabel(step)}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Additional Info */}
            {status.status === 'running' && (
                <div style={{ marginTop: '32px', padding: '16px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-md)', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    <Clock size={16} style={{ display: 'inline', marginRight: '8px' }} />
                    This may take 1-2 minutes depending on experiment duration
                </div>
            )}
        </div>
    );
};

