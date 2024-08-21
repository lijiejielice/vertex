import React from 'react';
import ConfigEditor from './components/ConfigEditor'; // Adjust the import path based on your project structure

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to Stock Monitor</h1>
      </header>
      <main>
        <ConfigEditor />
      </main>
    </div>
  );
}

export default App;
