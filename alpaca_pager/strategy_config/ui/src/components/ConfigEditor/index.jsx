import React, { useState } from 'react';
import './ConfigEditor.module.css'; // Importing CSS module for component-specific styling

const ConfigEditor = () => {
  const [config, setConfig] = useState({
    monitored_stocks: ['SPY', 'TSM', 'TSLA', 'NVDA'],
    alert_thresholds: {
      SPY: { lower_bound: 500, upper_bound: 550 },
      TSM: { lower_bound: 148, upper_bound: 180 },
      TSLA: { lower_bound: 210, upper_bound: 250 },
      NVDA: { lower_bound: 105, upper_bound: 120 },
    },
    poll_interval: 3600,
  });

  const handleAddStock = () => {
        const newStockCandidate = prompt('Enter stock symbol:');

        if (!newStockCandidate) {
          // User clicked cancel or entered an empty string
          return;
        }

        const newStock =  newStockCandidate.toUpperCase();
        if (!config.monitored_stocks.includes(newStock)) {
          setConfig({
            ...config,
            monitored_stocks: [...config.monitored_stocks, newStock],
            alert_thresholds: {
              ...config.alert_thresholds,
              [newStock]: { lower_bound: 0, upper_bound: 0 },
            },
          });
        } else {
          alert('Stock symbol already exists in the list.');
        }
      };


  const handleRemoveStock = (stock) => {
    const updatedStocks = config.monitored_stocks.filter(s => s !== stock);
    const updatedThresholds = { ...config.alert_thresholds };
    delete updatedThresholds[stock];
    setConfig({
      ...config,
      monitored_stocks: updatedStocks,
      alert_thresholds: updatedThresholds,
    });
  };

  const handleThresholdChange = (stock, bound, value) => {
    const updatedThresholds = {
      ...config.alert_thresholds,
      [stock]: {
        ...config.alert_thresholds[stock],
        [bound]: Number(value),
      },
    };
    setConfig({
      ...config,
      alert_thresholds: updatedThresholds,
    });
  };

  const handleSave = () => {
    // Example: send the updated config to a backend API
    console.log('Config saved:', config);
  };

  return (
    <div className="config-editor">
      <h2>Config Editor</h2>
      <div>
        <label>
          Poll Interval (seconds):
          <input
            type="number"
            value={config.poll_interval}
            onChange={(e) =>
              setConfig({ ...config, poll_interval: Number(e.target.value) })
            }
          />
        </label>
      </div>
      <h3>Monitored Stocks</h3>
      <ul>
        {config.monitored_stocks.map((stock) => (
          <li key={stock}>
            <span>{stock}</span>
            <button onClick={() => handleRemoveStock(stock)}>Remove</button>
            <div>
              <label>
                Lower Bound:
                <input
                  type="number"
                  value={config.alert_thresholds[stock].lower_bound}
                  onChange={(e) =>
                    handleThresholdChange(stock, 'lower_bound', e.target.value)
                  }
                />
              </label>
              <label>
                Upper Bound:
                <input
                  type="number"
                  value={config.alert_thresholds[stock].upper_bound}
                  onChange={(e) =>
                    handleThresholdChange(stock, 'upper_bound', e.target.value)
                  }
                />
              </label>
            </div>
          </li>
        ))}
      </ul>
      <button onClick={handleAddStock}>Add Stock</button>
      <button onClick={handleSave}>Save Config</button>
    </div>
  );
};

export default ConfigEditor;
