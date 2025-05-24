import { useState } from 'react';
import ParsingTable from './components/ParsingTable';

export default function App() {
  const [grammar, setGrammar] = useState('');
  const [first, setFirst] = useState('');
  const [follow, setFollow] = useState('');
  const [states, setStates] = useState('');
  const [table, setTable] = useState('');
  const [view, setView] = useState('FIRST'); // FIRST or FOLLOW
  const [section, setSection] = useState('SETS'); // SETS or STATES
  const [parser, setParser] = useState('SLR'); // SLR or LL1
  const [error, setError] = useState('');

  function parseTSVTable(tsvString) {
    const lines = tsvString.trim().split('\n');
    const headers = lines[0].split('\t');
    const rows = lines.slice(1).map(line => line.split('\t'));
    return { headers, rows };
  }

  const formatMap = (map) => {
    let output = '';
    for (const key in map) {
      output += `${key} : { ${map[key].join(', ')} }\n`;
    }
    return output;
  };

  const compute = async () => {
    setError('');
    try {
      const endpoint = parser === 'SLR' ? 'compute' : 'compute_ll1';
      const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grammar }),
      });
      const data = await response.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      setFirst(formatMap(data.FIRST));
      setFollow(formatMap(data.FOLLOW));
      setStates(data.STATES || '');
      const parsedTable = data.TABLE ? parseTSVTable(data.TABLE) : null;
      setTable(parsedTable);
    } catch (error) {
      console.error("Error computing grammar:", error);
      setError("Failed to compute grammar. Please try again.");
    }
  };

  const getContent = () => {
    if (section === 'SETS') {
      return view === 'FIRST' ? first : follow;
    }
    return states;
  };

  return (
    <div className="min-h-screen bg-green-50 p-8 font-sans">
      <h1 className="text-4xl font-bold text-center mb-10 text-gray-800">Parser Visualizer</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
        {/* Grammar Input */}
        <div className="bg-white p-6 rounded-lg shadow flex flex-col justify-between h-94">
          <div className="flex flex-col h-full">
            <div className="flex justify-between items-center mb-4">
              <label htmlFor="grammar" className="block font-semibold text-lg">Grammar</label>
              <div className="flex space-x-2">
                <button
                  onClick={() => setParser('SLR')}
                  className={`px-4 py-2 rounded-md font-medium ${
                    parser === 'SLR'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  SLR
                </button>
                <button
                  onClick={() => setParser('LL1')}
                  className={`px-4 py-2 rounded-md font-medium ${
                    parser === 'LL1'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  LL(1)
                </button>
              </div>
            </div>
            <textarea
              id="grammar"
              placeholder={parser === 'SLR' ? 
                `E → E + T | T\nT → T * F | F\nF → ( E ) | id` :
                `E → T E'\nE' → + T E' | ε\nT → F T'\nT' → * F T' | ε\nF → ( E ) | id`}
              className="w-full flex-grow p-4 text-base border border-gray-300 rounded-md resize-none"
              value={grammar}
              onChange={(e) => setGrammar(e.target.value)}
            />
            {error && (
              <div className="mt-2 p-2 bg-red-100 text-red-700 rounded-md">
                {error}
              </div>
            )}
            <button
              onClick={compute}
              className="mt-4 py-3 bg-blue-600 text-white text-lg font-semibold rounded-md hover:bg-blue-700 transition"
            >
              Compute
            </button>
          </div>
        </div>

        {/* Unified Output Box */}
        <div className="bg-white p-6 rounded-lg shadow h-94 flex flex-col justify-between">
          <div className="flex justify-between mb-4">
            {/* First/Follow Toggle */}
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setSection('SETS');
                  setView('FIRST');
                }}
                className={`px-4 py-2 rounded-md font-medium ${
                  section === 'SETS' && view === 'FIRST'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                FIRST
              </button>
              <button
                onClick={() => {
                  setSection('SETS');
                  setView('FOLLOW');
                }}
                className={`px-4 py-2 rounded-md font-medium ${
                  section === 'SETS' && view === 'FOLLOW'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                FOLLOW
              </button>
            </div>

            {/* States Toggle - Only show for SLR parser */}
            {parser === 'SLR' && (
              <div className="flex space-x-2">
                <button
                  onClick={() => setSection('STATES')}
                  className={`px-4 py-2 rounded-md font-medium ${
                    section === 'STATES'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  States & Items
                </button>
              </div>
            )}
          </div>

          <div className="bg-gray-100 border border-gray-300 rounded-md p-4 flex-grow overflow-y-auto whitespace-pre-wrap">
            {getContent()}
          </div>
        </div>
      </div>

      {/* Parse Table */}
      <div className="mt-10 bg-white p-6 rounded-lg shadow max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold mb-3">{parser} Parse Table</h2>
        <div className="overflow-x-auto">
          <ParsingTable table={table} />
        </div>
      </div>
    </div>
  );
}
