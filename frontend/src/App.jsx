import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios'

function App() {
  const [error, setError] = useState(null)

  const handleHttpRequest = async () => {
    try {
      const response = await axios.post(`/api/auth-token/`, {
        username: 'test',
        password: 'test',
      });
      console.log(response);
    } catch (error) {
      console.error('Error fetching data:', error);
      alert('Failed to fetch data from the server.');
      setError('Failed to fetch data from the server.');
    }
  }

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={handleHttpRequest}>
          count is 1
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
