import { useState } from 'react';
import { ExperimentForm } from './components/ExperimentForm';
import { ExperimentStatus } from './components/ExperimentStatus';
import { ResultsView } from './components/ResultsView';
import './index.css';

type AppState = 'form' | 'running' | 'results';

function App() {
  const [state, setState] = useState<AppState>('form');
  const [experimentId, setExperimentId] = useState<string | null>(null);

  const handleExperimentStart = (id: string) => {
    setExperimentId(id);
    setState('running');
  };

  const handleExperimentComplete = () => {
    setState('results');
  };

  const handleNewExperiment = () => {
    setExperimentId(null);
    setState('form');
  };

  return (
    <div className="app-layout">
      {/* Header */}
      <header className="header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginRight: 'auto' }}>
          <span style={{ fontWeight: 600, fontSize: '16px' }}>ChaosLab</span>
          <span style={{ color: 'var(--border)', fontSize: '16px' }}>/</span>
          <span style={{ color: 'var(--text-secondary)', fontSize: '16px' }}>Experiments</span>
        </div>
        
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <a href="#" style={{ fontSize: '14px', color: 'var(--text-secondary)', textDecoration: 'none' }}>Documentation</a>
          <a href="#" style={{ fontSize: '14px', color: 'var(--text-secondary)', textDecoration: 'none' }}>Support</a>
          <div style={{ width: '1px', height: '16px', background: 'var(--border)' }}></div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '8px', height: '8px', background: 'var(--success)', borderRadius: '50%' }}></div>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Operational</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {state === 'form' && (
          <div className="fade-in">
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 600, marginBottom: '8px' }}>New Experiment</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '16px' }}>
                Configure chaos parameters to test system resilience.
              </p>
            </div>
            <ExperimentForm onExperimentStart={handleExperimentStart} />
          </div>
        )}

        {state === 'running' && experimentId && (
          <ExperimentStatus
            experimentId={experimentId}
            onComplete={handleExperimentComplete}
          />
        )}

        {state === 'results' && experimentId && (
          <ResultsView experimentId={experimentId} onNewExperiment={handleNewExperiment} />
        )}
      </main>
    </div>
  );
}

export default App;
