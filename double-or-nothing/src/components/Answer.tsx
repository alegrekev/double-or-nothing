export default function Answer() {
    return (
        <div
            className="
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
                cursor-pointer
                transition-all duration-300 ease-out
                hover:-translate-y-1 hover:scale-[1.01]
                hover:shadow-[0_12px_34px_rgba(0,0,0,0.28)]
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
                    text-base font-semibold
                    text-black/75
                    drop-shadow-[0_1px_1px_rgba(255,255,255,0.45)]
                ">
                    A
                </div>

                <div className="
                    mt-2
                    text-sm sm:text-base
                    leading-relaxed
                    text-black/70
                ">
                    Push for early advancement. Continue working extra hours, volunteer for every challenging project, and network aggressively to impress superiors and peers. You're determined to make a significant mark in the first few months.
                </div>
            </div>
        </div>
    );
}
