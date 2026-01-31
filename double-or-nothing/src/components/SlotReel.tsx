import { useState, useEffect } from "react";

// University-themed emojis
const symbols = ["🎓", "🎰", "🏫", "📝"];

interface SlotReelProps {
  spinTrigger: number; // changes whenever we want to spin
}

export default function SlotReel({ spinTrigger }: SlotReelProps) {
  const [currentSymbols, setCurrentSymbols] = useState([symbols[0], symbols[1], symbols[2]]);

  useEffect(() => {
    // Spin all symbols randomly
    let spins = 10; // number of intermediate spins
    const interval = setInterval(() => {
      setCurrentSymbols([
        symbols[Math.floor(Math.random() * symbols.length)],
        symbols[Math.floor(Math.random() * symbols.length)],
        symbols[Math.floor(Math.random() * symbols.length)],
      ]);
      spins--;
      if (spins <= 0) clearInterval(interval);
    }, 50); // very fast spins
  }, [spinTrigger]);

  return (
    <div className="flex flex-col items-center justify-center mx-1 cursor-pointer">
      {currentSymbols.map((s, i) => (
        <div
          key={i}
          className="w-16 h-16 flex items-center justify-center text-4xl bg-white/20 rounded shadow animate-spin-slow"
        >
          {s}
        </div>
      ))}
    </div>
  );
}
