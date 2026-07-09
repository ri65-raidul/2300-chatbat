export default function SourceList({ sources }) {
    if (!sources || sources.length === 0) return null;

    return (
    <div className="mt-4 text-sm text-gray-400">
      <p className="mb-1">Sources:</p>

      <ul className="list-disc list-inside">
        {sources.map((source, index) => (
          <li key={index}>
            {source.source}, Page {source.page}
          </li>
        ))}
      </ul>
    </div>
  );
}