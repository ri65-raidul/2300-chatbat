"use client";

import { useState } from "react";

// Importing components
import MessageList from "@/components/MessageList";
import ChatInput from "@/components/ChatInput";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleAsk() {
    if(!question.trim()) return;

    const userQuestion = question;

    setMessages((prev) => [
      ...prev,
      {role: "user", text: userQuestion },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
        }),
      });


      if (!response.ok) {
        throw new Error("Failed to fetch response")
      }
      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {role: "assistant", text: data.answer, sources: data.sources },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Something went wrong." },
      ]);
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col p-8">
        <div className="mb-6">
          <h1 className="text-4xl font-bold mb-2">
            Chat with Bat
          </h1>

          <p className="text-gray-500">
            ECE 2300 ChatBot - Ask about course syllabus.
          </p>
        </div>

        <div className="flex-1">
          <MessageList
            messages={messages}
            loading={loading}
          />
        </div>

        <div className="border-t border-zinc-800 pt-4">
          <ChatInput
            question={question}
            setQuestion={setQuestion}
            handleAsk={handleAsk}
            loading={loading}
          />
        </div>
      </div>
    </main>
  );
}