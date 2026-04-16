import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-4">
      <div className="max-w-4xl w-full space-y-8 text-center">
        <header className="space-y-4">
          <h1 className="text-6xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            AI Scenario Trainer
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            A state-of-the-art multi-agent framework for advanced scenario simulation and temporal decay auditing.
          </p>
        </header>

        <main className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
          {['Graph Memory', 'Consensus Debate', 'Temporal Auditor'].map((feature) => (
            <div key={feature} className="p-6 bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700 hover:border-blue-500 transition-all cursor-pointer group">
              <h3 className="text-xl font-bold mb-2 group-hover:text-blue-400 transition-colors">{feature}</h3>
              <p className="text-slate-400 text-sm">
                Advanced {feature.toLowerCase()} engine for high-fidelity agent training.
              </p>
            </div>
          ))}
        </main>

        <footer className="pt-16">
          <button className="px-8 py-3 bg-blue-600 hover:bg-blue-500 rounded-full font-bold transition-all transform hover:scale-105 active:scale-95 shadow-lg shadow-blue-500/20">
            Launch Simulation
          </button>
        </footer>
      </div>
    </div>
  )
}

export default App
