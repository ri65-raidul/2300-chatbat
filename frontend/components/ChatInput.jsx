export default function ChatInput ({
    question,
    setQuestion,
    handleAsk,
    loading,
}) {
    return (
    <div className="rounded-2xl border border-zinc-700 bg-zinc-900 p-3">
      <textarea
        className="w-full resize-none bg-transparent outline-none text-white placeholder-gray-500"
        rows="3"
        placeholder="Ask about ECE2300..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleAsk();
          }
        }}
      />

      <div className="flex justify-end">
        <button
          className="rounded-xl bg-white px-4 py-2 text-sm font-medium text-black disabled:opacity-50"
          onClick={handleAsk}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}