from agent import run_agent, MODEL


# Fixed demo role controlled by the application.
CURRENT_ROLE = "customer"


def main():
    print("Safe Shopping Agent")
    print(f"Model: {MODEL}")
    print(f"Role: {CURRENT_ROLE}")
    print("Ask about products and stock.")
    print("Each request starts a fresh conversation.")
    print("Type 'exit' to quit.\n")

    try:
        while True:
            user_request = input("You: ").strip()

            if user_request.lower() == "exit":
                print("Goodbye!")
                break

            if not user_request:
                print("Please enter a request.\n")
                continue

            answer = run_agent(
                user_request=user_request,
                role=CURRENT_ROLE,
            )

            print(f"\nAssistant: {answer}\n")

    except (KeyboardInterrupt, EOFError):
        print("\nSession ended.")


if __name__ == "__main__":
    main()