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
            <div className="m-auto mt-10 w-200 flex items-center justify-center text-4xl font-bold">
                🎓 UNIVERSITY SIMULATOR 🎓
            </div>
            <Question />
            <div className="fixed top-10 right-10">
                <div className="flex" onClick={spinAll}>
                    <SlotReel spinTrigger={spinCount} />
                    <SlotReel spinTrigger={spinCount} />
                    <SlotReel spinTrigger={spinCount} />
                </div>
            </div>
            <div className="fixed bottom-10 left-1/2 -translate-x-1/2 items-center justify-center text-xl font-bold">
                Question 1/40
            </div>
        </div>
    )
}