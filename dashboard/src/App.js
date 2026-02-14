import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import './App.css';

function App() {
  const [stats, setStats] = useState(null);
  const [recentScans, setRecentScans] = useState([]);

  // Fetch Data from Python Backend
  useEffect(() => {
    // 1. Get Stats
    axios.get('http://127.0.0.1:8000/dashboard/stats')
      .then(res => setStats(res.data))
      .catch(err => console.error("Error fetching stats:", err));

    // 2. Get Recent Scans
    axios.get('http://127.0.0.1:8000/dashboard/recent')
      .then(res => setRecentScans(res.data))
      .catch(err => console.error("Error fetching recent:", err));
  }, []);

  if (!stats) return <div className="loading">Loading WADE Intelligence...</div>;

  // Data for the Pie Chart
  const chartData = [
    { name: 'Safe', value: stats.safe, color: '#00C49F' },
    { name: 'Phishing', value: stats.phishing, color: '#FF8042' },
    { name: 'Suspicious', value: stats.suspicious, color: '#FFBB28' }
  ];

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>🛡️ WADE Command Center</h1>
        <p>Real-time Threat Intelligence Dashboard</p>
      </header>

      {/* STATS CARDS */}
      <div className="stats-grid">
        <div className="card total">
          <h3>Total Scans</h3>
          <p>{stats.total_scans}</p>
        </div>
        <div className="card safe">
          <h3>Safe Sites</h3>
          <p>{stats.safe}</p>
        </div>
        <div className="card danger">
          <h3>Threats Blocked</h3>
          <p>{stats.phishing}</p>
        </div>
      </div>

      <div className="content-row">
        {/* CHART SECTION */}
        <div className="chart-section">
          <h2>Threat Distribution</h2>
          <PieChart width={400} height={300}>
            <Pie data={chartData} cx="50%" cy="50%" outerRadius={100} dataKey="value">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </div>

        {/* RECENT SCANS TABLE */}
        <div className="table-section">
          <h2>Recent Activity</h2>
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>URL</th>
                <th>Verdict</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {recentScans.map((scan) => (
                <tr key={scan._id} className={scan.verdict.toLowerCase()}>
                  <td>{new Date(scan.timestamp).toLocaleTimeString()}</td>
                  <td className="url-cell" title={scan.url}>{scan.url}</td>
                  <td>
                    <span className={`badge ${scan.verdict === 'Phishing' ? 'danger' : 'safe'}`}>
                      {scan.verdict}
                    </span>
                  </td>
                  <td>{scan.risk_score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;