import MessageBubble from "./MessageBubble";

import { useEffect, useRef } from "react";

export default function MessageList({messages, loading}){

    // Create a reference to the bottom of the chat
    const bottomRef = useRef(null);

    // Scroll to the bottom whenever the messages change
    useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages]);

    return (
        <div className="space-y-4 mb-6">
            {messages.map((message, index) => (
                <MessageBubble key={index} message={message} />
            ))}

            {loading && (
                <MessageBubble
                message={{
                    role: "assistant",
                    text: "Thinking...",
                }}
                />
            )}

            <div ref={bottomRef}></div>
        </div>
    );
}