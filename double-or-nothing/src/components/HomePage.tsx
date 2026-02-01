import { useState } from "react";

interface HomePageProps {
    onStart: () => void;
}

export default function HomePage({ onStart }: HomePageProps) {
    const [isHovered, setIsHovered] = useState(false);

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

            {/* Welcome Message */}
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
                        px-10 py-12
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
                    <div className="relative z-10 flex flex-col items-center">
                        <div className="
                            mb-8 text-center text-2xl sm:text-3xl
                            font-bold
                            text-black/80
                            drop-shadow-[0_1px_1px_rgba(255,255,255,0.4)]
                        ">
                            🎉 Congratulations! 🎉
                        </div>

                        <div className="
                            mb-6 text-center text-lg sm:text-xl
                            text-black/70
                            drop-shadow-[0_1px_1px_rgba(255,255,255,0.4)]
                            max-w-2xl
                            leading-relaxed
                        ">
                            You've been accepted to <span className="font-bold text-black/80">Hackviolet University!</span>
                        </div>

                        <div className="
                            mb-8 text-center text-base sm:text-lg
                            text-black/70
                            drop-shadow-[0_1px_1px_rgba(255,255,255,0.4)]
                            max-w-2xl
                            leading-relaxed
                        ">
                            Over the next four years your choices will shape your academic journey and your wellbeing.
                        </div>

                        <div className="
                            mb-10 text-center text-lg sm:text-xl
                            font-semibold
                            text-black/75
                            drop-shadow-[0_1px_1px_rgba(255,255,255,0.4)]
                        ">
                            Ready to start your freshman year?
                        </div>

                        {/* Yes Button */}
                        <button
                            onClick={onStart}
                            onMouseEnter={() => setIsHovered(true)}
                            onMouseLeave={() => setIsHovered(false)}
                            className="
                                group relative
                                px-12 py-4
                                text-xl
                                font-bold
                                rounded-2xl
                                bg-white/25
                                backdrop-blur-xl
                                border border-white/40
                                shadow-[0_8px_24px_rgba(0,0,0,0.22)]
                                overflow-hidden
                                cursor-pointer
                                transition-all duration-300 ease-out
                                hover:-translate-y-1 hover:scale-[1.05]
                                hover:shadow-[0_12px_34px_rgba(0,0,0,0.30)]
                            "
                        >
                            {/* liquid highlight */}
                            <div className="
                                absolute inset-0
                                bg-gradient-to-br from-white/60 via-white/10 to-transparent
                                opacity-70
                                pointer-events-none
                            " />

                            {/* hover sheen */}
                            <div className={`
                                absolute -left-1/2 top-0 h-full w-[200%]
                                bg-gradient-to-r from-transparent via-white/50 to-transparent
                                transition-all duration-500
                                pointer-events-none
                                ${isHovered ? 'opacity-40 translate-x-[30%]' : 'opacity-0 translate-x-[-30%]'}
                            `} />

                            <span className="
                                relative z-10
                                text-black/75
                                drop-shadow-[0_1px_1px_rgba(255,255,255,0.35)]
                            ">
                                Yes, Let's Begin! 🚀
                            </span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}