interface AnswerProps {
    text: string;
    onClick: () => void;
    disabled?: boolean;
}

export default function Answer({ text, onClick, disabled = false }: AnswerProps) {
    return (
        <div
            onClick={disabled ? undefined : onClick}
            className={`
                group relative
                flex-1
                min-h-[10rem]
                p-6
                rounded-2xl
                bg-white/20
                backdrop-blur-xl
                border border-white/40
                shadow-[0_8px_24px_rgba(0,0,0,0.20)]
                overflow-hidden
                transition-all duration-300 ease-out
                ${disabled 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'cursor-pointer hover:-translate-y-1 hover:scale-[1.01] hover:shadow-[0_12px_34px_rgba(0,0,0,0.28)]'
                }
            `}
        >
            {/* liquid highlight */}
            <div className="
                absolute inset-0
                bg-gradient-to-br from-white/60 via-white/10 to-transparent
                opacity-70
                pointer-events-none
            " />

            {/* hover sheen */}
            <div className="
                absolute -left-1/2 top-0 h-full w-[200%]
                bg-gradient-to-r from-transparent via-white/50 to-transparent
                opacity-0
                translate-x-[-30%]
                transition-all duration-500
                group-hover:opacity-40 group-hover:translate-x-[30%]
                pointer-events-none
            " />

            {/* content */}
            <div className="relative z-10 flex h-full flex-col justify-center text-center">
                <div className="
                    mt-2
                    text-sm sm:text-base
                    leading-relaxed
                    text-black/70
                ">
                    {text}
                </div>
            </div>
        </div>
    );
}