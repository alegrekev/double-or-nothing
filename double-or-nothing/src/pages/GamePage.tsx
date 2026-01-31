import Question from "../components/Question";

export default function GamePage() {
    return (
        <>
            <div className="m-auto mt-10 w-200 flex items-center justify-center text-4xl font-bold">
                UNIVERSITY SIMULATOR 🎰
            </div>
            <Question />
            <div className="fixed bottom-10 font-mono left-1/2 -translate-x-1/2 items-center justify-center text-xl font-bold">
                Question 1/40
            </div>
        </>
    )
}