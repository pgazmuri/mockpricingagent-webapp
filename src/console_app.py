import sys
import time

def main():
    # Force unbuffered output
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    
    print("Welcome to the Mock Pricing Agent Console Application!")
    print("=" * 50)
    
    while True:
        print("\nAvailable commands:")
        print("1. price - Calculate mock pricing")
        print("2. status - Show system status")
        print("3. help - Show this help menu")
        print("4. exit - Exit the application")
        
        try:
            # Use sys.stdout.write for the prompt without newline
            sys.stdout.write("\nEnter command: ")
            sys.stdout.flush()
            
            command = input().strip().lower()
            
            if command == "exit" or command == "quit":
                print("Goodbye!")
                break
            elif command == "price":
                handle_pricing()
            elif command == "status":
                handle_status()
            elif command == "help":
                show_help()
            elif command == "":
                continue
            else:
                print(f"Unknown command: {command}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

def handle_pricing():
    print("\n--- Mock Pricing Calculator ---")
    try:
        sys.stdout.write("Enter product name: ")
        sys.stdout.flush()
        product = input()
        
        sys.stdout.write("Enter quantity: ")
        sys.stdout.flush()
        quantity = input()
        
        if product and quantity.isdigit():
            base_price = 10.0
            total = float(quantity) * base_price
            print(f"\nProduct: {product}")
            print(f"Quantity: {quantity}")
            print(f"Unit Price: ${base_price:.2f}")
            print(f"Total Price: ${total:.2f}")
        else:
            print("Invalid input. Please enter a valid product name and numeric quantity.")
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")

def handle_status():
    print("\n--- System Status ---")
    print("Status: Online")
    print("Version: 1.0.0")
    print(f"Python Version: {sys.version.split()[0]}")
    print("Database: Connected")
    print("API: Ready")

def show_help():
    print("\n--- Help ---")
    print("This is a mock pricing agent console application.")
    print("Use the numbered commands to interact with the system.")
    print("Type 'exit' or 'quit' to close the application.")
    print("Press Ctrl+C to force exit at any time.")

if __name__ == "__main__":
    main()