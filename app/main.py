from .pipeline import answer
from .config import settings

def main():
    print("Text-to-SQL ready. Type 'exit' to quit.")
    while True:
        q = input("\nQuestion> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        full_question = q
        for _ in range(settings.max_clarify_rounds + 1):
            res = answer(full_question)
            if res.status != "needs_clarification":
                break
            for amb in res.clarifying_questions:
                opts = f" {amb.options}" if amb.options else ""
                reply = input(f"  ? {amb.question}{opts}\n  > ")
                full_question += f"\nClarification - '{amb.phrase}': {reply}"
        if res.status == "ok":
            print("\nSQL:", res.sql)
            if res.assumptions:
                print("Assumptions:", *res.assumptions, sep="\n  - ")
            print(res.columns)
            for r in res.rows[:20]:
                print(r)
        else:
            print(res.message)

if __name__ == "__main__":
    main()