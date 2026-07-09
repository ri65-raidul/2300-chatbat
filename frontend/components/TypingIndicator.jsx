export default function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2">
      <span
        className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce"
        style={{ animationDelay: "0ms" }}
      />
      <span
        className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce"
        style={{ animationDelay: "150ms" }}
      />
      <span
        className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce"
        style={{ animationDelay: "300ms" }}
      />
    </div>
  );
}