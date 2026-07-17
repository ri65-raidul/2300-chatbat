//import SourceList from "./SourceList";
import TypingIndicator from "./TypingIndicator";


export default function MessageBubble({ message }) {
    const isUser = message.role === "user"

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                isUser
                    ? "bg-blue-600 text-white"
                    : "bg-zinc-900 text-zinc-100 border border-zinc-800"
                }`}
            >
                <div className="whitespace-pre-wrap">
                    {message.text === "Thinking..." ? (
                        <TypingIndicator />
                    ) : (
                        <p>{message.text}</p>
                    )}
                </div>
            </div>
        </div>
    );
}