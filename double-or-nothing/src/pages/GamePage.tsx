import { useState, useEffect } from "react";
import Question from "../components/Question";

const API_BASE_URL = 'http://localhost:8000';

interface AnswerData {
    id: string;
    text: string;
}

interface QuestionData {
    question: string;
    year: string;
    major: string | null;
    answers: AnswerData[];
    question_number: number;
    total_questions: number;
    game_over: boolean;
    game_over_message: string | null;
}

export default function GamePage() {
    const [gameId, setGameId] = useState<string | null>(null);
    const [questionData, setQuestionData] = useState<QuestionData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Initialize game on mount
    useEffect(() => {
        initializeGame();
    }, []);

    const initializeGame = async () => {
        setLoading(true);
        setError(null);
        
        try {
            // Create new game
            const response = await fetch(`${API_BASE_URL}/api/game/new`, {
                method: 'POST',
            });
            
            if (!response.ok) {
                throw new Error('Failed to create game');
            }
            
            const data = await response.json();
            setGameId(data.game_id);

            // Get first question
            await fetchQuestion(data.game_id);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to initialize game');
            console.error('Failed to initialize game:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchQuestion = async (id: string) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/game/${id}/question`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch question');
            }
            
            const data: QuestionData = await response.json();
            setQuestionData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch question');
            console.error('Failed to fetch question:', err);
        }
    };

    const handleAnswerClick = async (answerId: string) => {
        if (!gameId || loading) return;
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/game/choice`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game_id: gameId,
                    choice_id: answerId,
                }),
            });
            
            if (!response.ok) {
                throw new Error('Failed to submit choice');
            }
            
            const data: QuestionData = await response.json();
            setQuestionData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to submit choice');
            console.error('Failed to submit choice:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleRestart = () => {
        setGameId(null);
        setQuestionData(null);
        setError(null);
        initializeGame();
    };

    if (error) {
        return (
            <div className="font-mono text-[rgb(147_129_255)]">
                <div className="m-auto mt-10 flex flex-col items-center justify-center min-h-screen">
                    <div className="bg-white/25 backdrop-blur-xl border border-white/40 rounded-2xl p-8 max-w-md">
                        <h2 className="text-2xl font-bold mb-4 text-red-600">Error</h2>
                        <p className="text-black/70 mb-4">{error}</p>
                        <button
                            onClick={handleRestart}
                            className="w-full px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition"
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!questionData || loading && !questionData) {
        return (
            <div className="font-mono text-[rgb(147_129_255)]">
                <div className="m-auto mt-10 flex items-center justify-center min-h-screen">
                    <div className="text-2xl text-black/70">Loading...</div>
                </div>
            </div>
        );
    }

    // Game over screen
    if (questionData.game_over) {
        return (
            <div className="font-mono text-[rgb(147_129_255)]">
                <div className="m-auto mt-10 flex flex-col items-center justify-center min-h-screen px-4">
                    <div className="
                        relative
                        bg-white/25
                        backdrop-blur-xl
                        border border-white/40
                        rounded-3xl
                        p-8
                        max-w-2xl
                        w-full
                        shadow-[0_8px_32px_rgba(0,0,0,0.25)]
                    ">
                        <h1 className="text-3xl font-bold mb-6 text-center text-black/70">
                            Game Over
                        </h1>
                        <p className="text-lg text-center mb-8 text-black/70 whitespace-pre-line">
                            {questionData.game_over_message || questionData.question}
                        </p>
                        <button
                            onClick={handleRestart}
                            className="w-full px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-bold rounded-lg transition"
                        >
                            Play Again
                        </button>
                    </div>
                </div>
            </div>
        );
    }

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
                        🎓 COLLEGE SIMULATOR 🎓
                    </span>
                </div>
            </div>

            <Question
                questionText={questionData.question}
                answers={questionData.answers}
                onAnswerClick={handleAnswerClick}
                disabled={loading}
            />

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

                    {/* subtle sheen */}
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
                        Question {questionData.question_number}/{questionData.total_questions}
                    </span>
                </div>
            </div>
        </div>
    );
}