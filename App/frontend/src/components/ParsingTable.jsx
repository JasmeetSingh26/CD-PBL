export default function ParsingTable({ table }) {
  if (!table || !table.headers || !table.rows) {
    return <p className="text-center text-gray-500">No parsing table available.</p>;
  }

  const getCellClass = (value) => {
    if (!value) return '';
    const val = value.toLowerCase();
    if (val.startsWith('s')) return 'bg-blue-100 text-blue-900 font-medium';
    if (val.startsWith('r')) return 'bg-yellow-100 text-yellow-900 font-medium';
    if (val === 'acc' || val === 'accept') return 'bg-green-100 text-green-900 font-semibold';
    // For LL(1) productions
    if (val.includes('->')) return 'bg-purple-100 text-purple-900 font-medium';
    return '';
  };

  return (
    <div className="relative overflow-x-auto max-h-[500px] overflow-y-auto border rounded-md">
      <table className="table-auto border-collapse border border-gray-300 w-full text-sm text-center">
        <thead className="sticky top-0 bg-gray-100 z-10 shadow-sm">
          <tr>
            {table.headers.map((header, i) => (
              <th
                key={i}
                className="border border-gray-300 px-3 py-2 font-semibold text-gray-700"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, i) => (
            <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              {row.map((cell, j) => (
                <td
                  key={j}
                  className={`border border-gray-300 px-3 py-2 whitespace-nowrap ${getCellClass(cell)}`}
                >
                  {cell || '\u00A0'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
