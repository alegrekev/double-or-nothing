import Answer from "./Answer";

interface QuestionProps {
    questionText: string;
    answers: Array<{ id: string; text: string }>;
    onAnswerClick: (answerId: string) => void;
    disabled?: boolean;
}

export default function Question({ questionText, answers, onAnswerClick, disabled = false }: QuestionProps) {
    return (
        <div className="m-auto mt-24 flex w-[70rem] justify-center">
            <div
                className="
                    relative
                    w-full
                    rounded-3xl
                    bg-white/20
                    backdrop-blur-xl
                    border border-white/40
                    shadow-[0_8px_32px_rgba(0,0,0,0.25)]
                    px-10 py-8
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

                {/* moving sheen */}
                <div className="
                    absolute -left-1/2 top-0 h-full w-[200%]
                    bg-gradient-to-r from-transparent via-white/40 to-transparent
                    opacity-30
                    animate-[sheen_7s_linear_infinite]
                    pointer-events-none
                " />

                {/* content */}
                <div className="relative z-10">
                    <div className="
                        mb-8 text-center text-lg 
                        text-black/70
                        drop-shadow-[0_1px_1px_rgba(255,255,255,0.4)]
                    ">
                        {questionText}
                    </div>

                    <div className="flex justify-center gap-8">
                        {answers.map((answer) => (
                            <Answer
                                key={answer.id}
                                text={answer.text}
                                onClick={() => onAnswerClick(answer.id)}
                                disabled={disabled}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}