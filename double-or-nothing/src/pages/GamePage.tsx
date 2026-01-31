import { useState } from "react";
import Question from "../components/Question";
import SlotReel from "../components/SlotReel";

export default function GamePage() {
    const [spinCount, setSpinCount] = useState(0);

    const spinAll = () => {
        setSpinCount(spinCount + 1); // triggers all reels
    };

    return (
        <div className="font-mono text-[rgb(147_129_255)]">
            <div className="m-auto mt-10 flex justify-center">
                <div className="
        relative
        px-12 py-4
        text-2xl sm:text-3xl md:text-4xl
        font-bold tracking-wide
        rounded-full
        bg-white/25
        backdrop-blur-xl
        border border-white/40
        shadow-[0_8px_32px_rgba(0,0,0,0.25)]
        text-[rgb(147_129_255)]
        overflow-hidden
    ">
                    {/* liquid highlight */}
                    <div className="
            absolute inset-0
            bg-gradient-to-br from-white/60 via-white/10 to-transparent
            opacity-70
            pointer-events-none
        " />

                    {/* moving sheen */}
                    <div className="
            absolute -left-1/2 top-0 h-full w-[200%]
            bg-gradient-to-r from-transparent via-white/40 to-transparent
            opacity-30
            animate-[sheen_6s_linear_infinite]
            pointer-events-none
        " />

                    <span className="
    relative z-10
    text-black/70
    drop-shadow-[0_1px_1px_rgba(0,0,0,0.35)]
">
                        🎓 UNIVERSITY SIMULATOR 🎓
                    </span>

                </div>
            </div>



            <Question />
            <div className="fixed bottom-10 left-1/2 -translate-x-1/2">
                <div
                    className="
            relative
            px-6 py-3
            rounded-full
            bg-white/20
            backdrop-blur-xl
            border border-white/40
            shadow-[0_8px_24px_rgba(0,0,0,0.22)]
            overflow-hidden
        "
                >
                    {/* liquid highlight */}
                    <div className="
            absolute inset-0
            bg-gradient-to-br from-white/60 via-white/10 to-transparent
            opacity-70
            pointer-events-none
        " />

                    {/* subtle sheen (slower + lighter than title) */}
                    <div className="
            absolute -left-1/2 top-0 h-full w-[200%]
            bg-gradient-to-r from-transparent via-white/40 to-transparent
            opacity-20
            animate-[sheen_10s_linear_infinite]
            pointer-events-none
        " />

                    <span className="
            relative z-10
            text-sm sm:text-base
            font-semibold
            text-black/70
            drop-shadow-[0_1px_1px_rgba(255,255,255,0.35)]
            tracking-wide
        ">
                        Question 1/40
                    </span>
                </div>
            </div>

        </div>
    )
}