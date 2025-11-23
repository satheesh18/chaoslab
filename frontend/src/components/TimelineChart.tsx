import React from 'react';
import type { TimelineDataPoint } from '../api/client';

interface TimelineChartProps {
    timeline: TimelineDataPoint[];
}

export const TimelineChart: React.FC<TimelineChartProps> = ({ timeline }) => {
    if (!timeline || timeline.length === 0) {
        return null;
    }

    // Calculate max values for scaling
    const maxCpu = Math.max(...timeline.map(p => p.cpu), 100);
    const maxMemory = Math.max(...timeline.map(p => p.memory), 100);
    const maxTime = Math.max(...timeline.map(p => p.time_offset));

    // Chart dimensions
    const chartWidth = 800;
    const chartHeight = 300;
    const padding = { top: 20, right: 60, bottom: 40, left: 60 };
    const plotWidth = chartWidth - padding.left - padding.right;
    const plotHeight = chartHeight - padding.top - padding.bottom;

    // Helper to convert data to SVG coordinates
    const getX = (timeOffset: number) => {
        return padding.left + (timeOffset / maxTime) * plotWidth;
    };

    const getY = (value: number, max: number) => {
        return padding.top + plotHeight - (value / max) * plotHeight;
    };

    // Generate path for CPU line
    const cpuPath = timeline
        .map((point, i) => {
            const x = getX(point.time_offset);
            const y = getY(point.cpu, maxCpu);
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        })
        .join(' ');

    // Generate path for Memory line
    const memoryPath = timeline
        .map((point, i) => {
            const x = getX(point.time_offset);
            const y = getY(point.memory, maxMemory);
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        })
        .join(' ');

    // Generate error markers
    const errorPoints = timeline.filter(p => p.error_count > 0);

    return (
        <div className="card" style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.5rem' }}>📊</span>
                <h3 style={{ marginBottom: 0 }}>Metrics Timeline</h3>
            </div>

            <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: 20, height: 3, background: '#3b82f6' }} />
                    <span>CPU Usage</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: 20, height: 3, background: '#10b981' }} />
                    <span>Memory Usage</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: 12, height: 12, background: '#ef4444', borderRadius: '50%' }} />
                    <span>Errors</span>
                </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
                <svg
                    width={chartWidth}
                    height={chartHeight}
                    style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}
                >
                    {/* Grid lines */}
                    {[0, 25, 50, 75, 100].map((percent) => {
                        const y = getY(percent, 100);
                        return (
                            <g key={percent}>
                                <line
                                    x1={padding.left}
                                    y1={y}
                                    x2={chartWidth - padding.right}
                                    y2={y}
                                    stroke="var(--border)"
                                    strokeWidth="1"
                                    strokeDasharray="4"
                                />
                                <text
                                    x={padding.left - 10}
                                    y={y + 4}
                                    textAnchor="end"
                                    fontSize="12"
                                    fill="var(--text-muted)"
                                >
                                    {percent}%
                                </text>
                            </g>
                        );
                    })}

                    {/* Time axis labels */}
                    {timeline
                        .filter((_, i) => i % Math.max(1, Math.floor(timeline.length / 6)) === 0)
                        .map((point) => {
                            const x = getX(point.time_offset);
                            return (
                                <text
                                    key={point.time_offset}
                                    x={x}
                                    y={chartHeight - padding.bottom + 20}
                                    textAnchor="middle"
                                    fontSize="12"
                                    fill="var(--text-muted)"
                                >
                                    {point.time_offset}s
                                </text>
                            );
                        })}

                    {/* CPU line */}
                    <path d={cpuPath} fill="none" stroke="#3b82f6" strokeWidth="2.5" />

                    {/* Memory line */}
                    <path d={memoryPath} fill="none" stroke="#10b981" strokeWidth="2.5" />

                    {/* Error markers */}
                    {errorPoints.map((point, i) => {
                        const x = getX(point.time_offset);
                        const y = padding.top;
                        return (
                            <g key={i}>
                                <line
                                    x1={x}
                                    y1={y}
                                    x2={x}
                                    y2={chartHeight - padding.bottom}
                                    stroke="#ef4444"
                                    strokeWidth="1"
                                    strokeDasharray="3"
                                    opacity="0.5"
                                />
                                <circle cx={x} cy={y} r="5" fill="#ef4444" />
                                <text
                                    x={x}
                                    y={y - 10}
                                    textAnchor="middle"
                                    fontSize="11"
                                    fill="#ef4444"
                                    fontWeight="bold"
                                >
                                    {point.error_count}
                                </text>
                            </g>
                        );
                    })}

                    {/* Axis labels */}
                    <text
                        x={chartWidth / 2}
                        y={chartHeight - 5}
                        textAnchor="middle"
                        fontSize="13"
                        fill="var(--text-primary)"
                        fontWeight="500"
                    >
                        Time (seconds)
                    </text>
                    <text
                        x={15}
                        y={chartHeight / 2}
                        textAnchor="middle"
                        fontSize="13"
                        fill="var(--text-primary)"
                        fontWeight="500"
                        transform={`rotate(-90 15 ${chartHeight / 2})`}
                    >
                        Usage (%)
                    </text>
                </svg>
            </div>

            {/* Stats summary */}
            <div
                style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: '1rem',
                    marginTop: '1rem',
                    fontSize: '0.875rem',
                }}
            >
                <div>
                    <span style={{ color: 'var(--text-muted)' }}>Data Points: </span>
                    <strong>{timeline.length}</strong>
                </div>
                <div>
                    <span style={{ color: 'var(--text-muted)' }}>Duration: </span>
                    <strong>{maxTime}s</strong>
                </div>
                <div>
                    <span style={{ color: 'var(--text-muted)' }}>Sampling: </span>
                    <strong>~{Math.round(maxTime / timeline.length)}s intervals</strong>
                </div>
            </div>
        </div>
    );
};
