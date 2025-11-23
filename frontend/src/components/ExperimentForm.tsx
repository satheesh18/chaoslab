import React, { useState } from 'react';
import { Play, Zap } from 'lucide-react';
import { chaosLabAPI, type StartExperimentRequest } from '../api/client';

interface ExperimentFormProps {
    onExperimentStart: (experimentId: string) => void;
}

const CHAOS_SCENARIOS = [
    {
        id: 'network_delay',
        name: 'Network Delay',
        description: 'Adds 300ms latency to test timeout handling',
        icon: '🌐',
    },
    {
        id: 'memory_pressure',
        name: 'Memory Pressure',
        description: 'Fills 80% RAM to test resource management',
        icon: '💾',
    },
    {
        id: 'disk_full',
        name: 'Disk Full',
        description: 'Fills disk space to test error handling',
        icon: '💿',
    },
    {
        id: 'process_kill',
        name: 'Process Kill',
        description: 'Randomly kills processes to test recovery',
        icon: '⚡',
    },
    {
        id: 'dependency_failure',
        name: 'Dependency Failure',
        description: 'Mocks DNS/DB failures to test resilience',
        icon: '🔌',
    },
];

export const ExperimentForm: React.FC<ExperimentFormProps> = ({ onExperimentStart }) => {
    const [selectedScenario, setSelectedScenario] = useState('network_delay');
    const [duration, setDuration] = useState(60);
    const [intensity, setIntensity] = useState<'low' | 'medium' | 'high'>('medium');
    const [numInstances, setNumInstances] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const request: StartExperimentRequest = {
                scenario: selectedScenario,
                config: {
                    duration,
                    intensity,
                    num_instances: numInstances,
                },
            };

            const response = await chaosLabAPI.startExperiment(request);
            onExperimentStart(response.experiment_id);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to start experiment');
            console.error('Error starting experiment:', err);
        } finally {
            setLoading(false);
        }
    };

    const selectedScenarioData = CHAOS_SCENARIOS.find(s => s.id === selectedScenario);

    return (
        <div className="panel fade-in" style={{ padding: '32px' }}>
            <form onSubmit={handleSubmit}>
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '48px' }}>
                    {/* Left Column: Scenarios */}
                    <div>
                        <label className="text-xs text-muted" style={{ display: 'block', marginBottom: '16px', fontWeight: 600, textTransform: 'uppercase' }}>
                            Select Scenario
                        </label>
                        <div className="grid-cols-3">
                            {CHAOS_SCENARIOS.map((scenario) => (
                                <div
                                    key={scenario.id}
                                    onClick={() => setSelectedScenario(scenario.id)}
                                    style={{
                                        padding: '16px',
                                        background: selectedScenario === scenario.id ? 'var(--bg-subtle)' : 'transparent',
                                        border: `1px solid ${selectedScenario === scenario.id ? 'var(--text-primary)' : 'var(--border)'}`,
                                        borderRadius: 'var(--radius-md)',
                                        cursor: 'pointer',
                                        transition: 'all 0.15s ease',
                                        height: '100%'
                                    }}
                                >
                                    <div style={{ fontSize: '24px', marginBottom: '12px' }}>{scenario.icon}</div>
                                    <div style={{ fontSize: '14px', fontWeight: 500, marginBottom: '4px', color: 'var(--text-primary)' }}>
                                        {scenario.name}
                                    </div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                                        {scenario.description}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Right Column: Configuration */}
                    <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: '48px' }}>
                        <label className="text-xs text-muted" style={{ display: 'block', marginBottom: '24px', fontWeight: 600, textTransform: 'uppercase' }}>
                            Configuration
                        </label>

                        <div style={{ marginBottom: '32px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                <label className="text-sm">Duration</label>
                                <span className="text-sm font-mono">{duration}s</span>
                            </div>
                            <input
                                type="range"
                                min="10"
                                max="300"
                                step="10"
                                value={duration}
                                onChange={(e) => setDuration(Number(e.target.value))}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                                <span className="text-xs text-muted">10s</span>
                                <span className="text-xs text-muted">300s</span>
                            </div>
                        </div>

                        <div style={{ marginBottom: '32px' }}>
                            <label className="text-sm" style={{ display: 'block', marginBottom: '12px' }}>Intensity</label>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
                                {(['low', 'medium', 'high'] as const).map((level) => (
                                    <button
                                        key={level}
                                        type="button"
                                        onClick={() => setIntensity(level)}
                                        style={{
                                            padding: '8px',
                                            textTransform: 'capitalize',
                                            background: intensity === level ? 'var(--text-primary)' : 'transparent',
                                            color: intensity === level ? 'var(--bg-root)' : 'var(--text-secondary)',
                                            border: `1px solid ${intensity === level ? 'var(--text-primary)' : 'var(--border)'}`,
                                            borderRadius: 'var(--radius-sm)',
                                            cursor: 'pointer',
                                            fontSize: '13px',
                                            fontWeight: 500,
                                            transition: 'all 0.15s ease'
                                        }}
                                    >
                                        {level}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div style={{ marginBottom: '48px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                <label className="text-sm">Parallel Instances</label>
                                <span className="text-sm font-mono">{numInstances}x</span>
                            </div>
                            <input
                                type="range"
                                min="1"
                                max="5"
                                step="1"
                                value={numInstances}
                                onChange={(e) => setNumInstances(Number(e.target.value))}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                                <span className="text-xs text-muted">1 instance</span>
                                <span className="text-xs text-muted">5 instances</span>
                            </div>
                            {numInstances > 1 && (
                                <div style={{ marginTop: '8px', padding: '8px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)', fontSize: '12px', color: 'var(--text-secondary)' }}>
                                    ℹ️ Metrics will be averaged across all instances
                                </div>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="btn btn-primary"
                            style={{ width: '100%' }}
                        >
                            {loading ? (
                                <>
                                    <div className="spinner" />
                                    <span>Initializing...</span>
                                </>
                            ) : (
                                <>
                                    <Play size={16} fill="currentColor" />
                                    <span>Start Experiment</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

