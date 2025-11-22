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
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1>🧠 ChaosLab</h1>
          <p>
            Safe chaos engineering with E2B sandboxes, Groq AI analysis, and Grafana visualization
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container" style={{ position: 'relative', zIndex: 10 }}>
        {state === 'form' && <ExperimentForm onExperimentStart={handleExperimentStart} />}

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

      {/* Footer */}
      <footer
        style={{
          textAlign: 'center',
          padding: '2rem',
          color: 'var(--text-muted)',
          fontSize: '0.875rem',
          position: 'relative',
          zIndex: 10,
        }}
      >
        <p>
          Built with E2B • Groq • Grafana MCP • React • TypeScript
        </p>
      </footer>
    </div>
  );
}

export default App;
