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
        <div className="card fade-in">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <Zap size={32} color="#6366f1" />
                <h2 style={{ marginBottom: 0 }}>Configure Chaos Experiment</h2>
            </div>

            <form onSubmit={handleSubmit}>
                {/* Scenario Selection */}
                <div className="form-group">
                    <label className="form-label">Chaos Scenario</label>
                    <div className="grid grid-2" style={{ gap: '1rem' }}>
                        {CHAOS_SCENARIOS.map((scenario) => (
                            <div
                                key={scenario.id}
                                onClick={() => setSelectedScenario(scenario.id)}
                                style={{
                                    padding: '1rem',
                                    background: selectedScenario === scenario.id ? 'var(--bg-hover)' : 'var(--bg-tertiary)',
                                    border: `2px solid ${selectedScenario === scenario.id ? 'var(--accent-primary)' : 'var(--border)'}`,
                                    borderRadius: 'var(--radius-md)',
                                    cursor: 'pointer',
                                    transition: 'all var(--transition-base)',
                                }}
                            >
                                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{scenario.icon}</div>
                                <div style={{ fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-primary)' }}>
                                    {scenario.name}
                                </div>
                                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                    {scenario.description}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Duration */}
                <div className="form-group">
                    <label className="form-label">
                        Duration: {duration} seconds
                    </label>
                    <input
                        type="range"
                        min="10"
                        max="300"
                        step="10"
                        value={duration}
                        onChange={(e) => setDuration(Number(e.target.value))}
                        style={{
                            width: '100%',
                            height: '8px',
                            background: 'var(--bg-tertiary)',
                            borderRadius: 'var(--radius-lg)',
                            outline: 'none',
                            cursor: 'pointer',
                        }}
                    />
                </div>

                {/* Intensity */}
                <div className="form-group">
                    <label className="form-label">Intensity</label>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        {(['low', 'medium', 'high'] as const).map((level) => (
                            <button
                                key={level}
                                type="button"
                                onClick={() => setIntensity(level)}
                                className={intensity === level ? 'btn-primary' : 'btn-secondary'}
                                style={{
                                    flex: 1,
                                    padding: '0.75rem',
                                    textTransform: 'capitalize',
                                }}
                            >
                                {level}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Error Display */}
                {error && (
                    <div
                        style={{
                            padding: '1rem',
                            background: 'rgba(239, 68, 68, 0.1)',
                            border: '1px solid rgba(239, 68, 68, 0.2)',
                            borderRadius: 'var(--radius-md)',
                            color: 'var(--error)',
                            marginBottom: '1rem',
                        }}
                    >
                        {error}
                    </div>
                )}

                {/* Submit Button */}
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                    style={{
                        width: '100%',
                        padding: '1rem',
                        fontSize: '1.125rem',
                        justifyContent: 'center',
                    }}
                >
                    {loading ? (
                        <>
                            <span className="spinner" />
                            Starting Experiment...
                        </>
                    ) : (
                        <>
                            <Play size={20} />
                            Start Chaos Experiment
                        </>
                    )}
                </button>
            </form>

            {/* Selected Scenario Info */}
            {selectedScenarioData && (
                <div
                    style={{
                        marginTop: '1.5rem',
                        padding: '1rem',
                        background: 'var(--bg-tertiary)',
                        borderRadius: 'var(--radius-md)',
                        borderLeft: '4px solid var(--accent-primary)',
                    }}
                >
                    <div style={{ fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                        {selectedScenarioData.icon} {selectedScenarioData.name}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                        {selectedScenarioData.description}
                    </div>
                </div>
            )}
        </div>
    );
};
