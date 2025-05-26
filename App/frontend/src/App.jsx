import { useState } from "react";
import ParsingTable from "./components/ParsingTable";

export default function App() {
  const [grammar, setGrammar] = useState("");
  const [inputString, setInputString] = useState("");
  const [first, setFirst] = useState("");
  const [follow, setFollow] = useState("");
  const [states, setStates] = useState("");
  const [table, setTable] = useState("");
  const [view, setView] = useState("FIRST"); // FIRST or FOLLOW
  const [section, setSection] = useState("SETS"); // SETS or STATES
  const [parser, setParser] = useState("CLR"); // CLR or LL1
  const [error, setError] = useState("");
  const [parsingResult, setParsingResult] = useState(null);
  const [isParsing, setIsParsing] = useState(false);

  function parseTSVTable(tsvString) {
    const lines = tsvString.trim().split("\n");
    const headers = lines[0].split("\t");
    const rows = lines.slice(1).map((line) => line.split("\t"));
    return { headers, rows };
  }

  const formatMap = (map) => {
    let output = "";
    for (const key in map) {
      output += `${key} : { ${map[key].join(", ")} }\n`;
    }
    return output;
  };

  const compute = async (parseInput = false) => {
    setError("");
    setParsingResult(null);
    try {
      const endpoint = parser === "CLR" ? "compute" : "compute_ll1";
      const payload = { grammar };

      // Include input string if we want to parse it
      if (parseInput && inputString) {
        payload.input_string = inputString;
      }

      const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      setFirst(formatMap(data.FIRST));
      setFollow(formatMap(data.FOLLOW));
      setStates(data.STATES || "");
      const parsedTable = data.TABLE ? parseTSVTable(data.TABLE) : null;
      setTable(parsedTable);

      // If we sent an input string, store the parsing result
      if (parseInput && inputString && data.PARSING_RESULT) {
        setParsingResult(data.PARSING_RESULT);
      }
    } catch (error) {
      console.error("Error computing grammar:", error);
      setError("Failed to compute grammar. Please try again.");
    }
  };

  const parseInputString = async () => {
    if (!inputString) {
      setError("Please enter an input string to parse");
      return;
    }
    setIsParsing(true);
    await compute(true);
    setIsParsing(false);
  };

  const getContent = () => {
    if (section === "SETS") {
      return view === "FIRST" ? first : follow;
    }
    return states;
  };

  return (
    <div className="min-h-screen bg-green-50 p-8 font-sans">
      <h1 className="text-4xl font-bold text-center mb-10 text-gray-800">
        Parser Visualizer
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
        {/* Grammar Input */}
        <div className="bg-white p-6 rounded-lg shadow flex flex-col justify-between h-94">
          <div className="flex flex-col h-full">
            <div className="flex justify-between items-center mb-4">
              <label htmlFor="grammar" className="block font-semibold text-lg">
                Grammar
              </label>
              <div className="flex space-x-2">
                <button
                  onClick={() => setParser("CLR")}
                  className={`px-4 py-2 rounded-md font-medium ${
                    parser === "CLR"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-800"
                  }`}
                >
                  CLR
                </button>
                <button
                  onClick={() => setParser("LL1")}
                  className={`px-4 py-2 rounded-md font-medium ${
                    parser === "LL1"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-800"
                  }`}
                >
                  LL(1)
                </button>
              </div>
            </div>
            <textarea
              id="grammar"
              placeholder={
                parser === "CLR"
                  ? `E → E + T | T\nT → T * F | F\nF → ( E ) | id`
                  : `E → T E'\nE' → + T E' | ε\nT → F T'\nT' → * F T' | ε\nF → ( E ) | id`
              }
              className="w-full flex-grow p-4 text-base border border-gray-300 rounded-md resize-none"
              value={grammar}
              onChange={(e) => setGrammar(e.target.value)}
            />
            {error && (
              <div className="mt-2 p-2 bg-red-100 text-red-700 rounded-md">
                {error}
              </div>
            )}
            <div className="flex space-x-2 mt-4">
              <button
                onClick={() => compute(false)}
                className="py-3 bg-blue-600 text-white text-lg font-semibold rounded-md hover:bg-blue-700 transition flex-1"
              >
                Compute
              </button>
              <button
                onClick={parseInputString}
                disabled={isParsing}
                className={`py-3 bg-green-600 text-white text-lg font-semibold rounded-md hover:bg-green-700 transition flex-1 ${
                  isParsing ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                {isParsing ? "Parsing..." : "Parse Input"}
              </button>
            </div>
          </div>
        </div>

        {/* Unified Output Box */}
        <div className="bg-white p-6 rounded-lg shadow h-94 flex flex-col justify-between">
          <div className="flex justify-between mb-4">
            {/* First/Follow Toggle */}
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setSection("SETS");
                  setView("FIRST");
                }}
                className={`px-4 py-2 rounded-md font-medium ${
                  section === "SETS" && view === "FIRST"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                FIRST
              </button>
              <button
                onClick={() => {
                  setSection("SETS");
                  setView("FOLLOW");
                }}
                className={`px-4 py-2 rounded-md font-medium ${
                  section === "SETS" && view === "FOLLOW"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                FOLLOW
              </button>
            </div>

            {/* States Toggle - Only show for CLR parser */}
            {parser === "CLR" && (
              <div className="flex space-x-2">
                <button
                  onClick={() => setSection("STATES")}
                  className={`px-4 py-2 rounded-md font-medium ${
                    section === "STATES"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-800"
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

      {/* Input String Section */}
      <div className="mt-6 bg-white p-6 rounded-lg shadow max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold mb-3">Input String</h2>
        <div className="flex items-center space-x-4">
          <input
            type="text"
            placeholder="Enter string to parse (e.g., id+id*id)"
            className="flex-grow p-3 border border-gray-300 rounded-md"
            value={inputString}
            onChange={(e) => setInputString(e.target.value)}
          />
          <button
            onClick={parseInputString}
            disabled={isParsing}
            className={`px-6 py-3 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 ${
              isParsing ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {isParsing ? "Parsing..." : "Parse"}
          </button>
        </div>
      </div>

      {/* Parse Table */}
      <div className="mt-6 bg-white p-6 rounded-lg shadow max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold mb-3">{parser} Parse Table</h2>
        <div className="overflow-x-auto">
          <ParsingTable table={table} />
        </div>
      </div>

      {/* Parsing Result */}
      {parsingResult && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow max-w-6xl mx-auto">
          <h2 className="text-2xl font-semibold mb-3">
            Parsing Result:{" "}
            {parsingResult.success ? (
              <span className="text-green-600">Accepted</span>
            ) : (
              <span className="text-red-600">Rejected</span>
            )}
          </h2>
          <p className="mb-4">{parsingResult.message}</p>

          <div className="overflow-x-auto">
            <table className="min-w-full border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-3 border text-left">Step</th>
                  <th className="p-3 border text-left">Stack</th>
                  <th className="p-3 border text-left">Input</th>
                  <th className="p-3 border text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {parsingResult.steps.map((step, index) => (
                  <tr key={index} className="border">
                    <td className="p-3 border">{index + 1}</td>
                    <td className="p-3 border font-mono">{step.stack}</td>
                    <td className="p-3 border font-mono">{step.input}</td>
                    <td className="p-3 border">{step.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
