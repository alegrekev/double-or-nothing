import Answer from "./Answer";

export default function Question() {
    return (
        <>
            <div className="m-auto mt-25 w-100 flex items-center justify-center text-2xl font-bold">
                Question
            </div>
            <div className="m-auto mt-10 w-230 flex items-center justify-center">
                <Answer />
                <Answer />
            </div>
        </>
    )
}