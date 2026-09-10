import os
import json
import random

BANK_FILE = "bank.json"

def load_accounts():
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_accounts(data):
    with open(BANK_FILE, "w") as f:
        json.dump(data, f, indent=4)


def generate_account_number(existing_data):
    existing_numbers = {acc["account"] for acc in existing_data}
    while True:
        number = str(random.randint(100000, 999999))
        if number not in existing_numbers:
            return number

class BankAccount:
    def __init__(self, name, account, pin, balance=0, transactions=None):
        self.name = name
        self.account = account
        self.pin = pin
        self.balance = balance
        self.transactions = transactions if transactions is not None else []

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transactions.append(f"Deposited ${amount:.2f}")
            print(f"\n✅ Successfully deposited ${amount:.2f}")
            return True
        else:
            print("\n❌ Invalid amount")
            return False

    def withdraw(self, amount):
        if amount <= 0:
            print("\n❌ Invalid withdrawal amount")
            return False
        elif amount > self.balance:
            print("\n❌ Insufficient balance")
            return False
        else:
            self.balance -= amount
            self.transactions.append(f"Withdrawn ${amount:.2f}")
            print(f"\n✅ Successfully withdrawn ${amount:.2f}")
            return True

    def check_balance(self):
        print(f"\n💰 Current balance: ${self.balance:.2f}")

    def show_transactions(self):
        print("\n📜 Transaction History:")
        if not self.transactions:
            print("No transactions have been made yet.")
        else:
            for transaction in self.transactions:
                print(transaction)

    def change_pin(self, new_pin):
        self.pin = new_pin
        print("\n✅ PIN changed successfully")

    def to_dict(self):
        return {
            "name": self.name,
            "account": self.account,
            "pin": self.pin,
            "balance": self.balance,
            "transactions": self.transactions,
        }


class BankingApp:
    def __init__(self):
        print("🏦 Welcome to the Banking System")
        self.data = load_accounts()
        self.current_account = None  # BankAccount currently logged in

    def _find_account_index(self, account_number):
        for i, acc in enumerate(self.data):
            if acc["account"] == account_number:
                return i
        return None

    def save_current_account(self):
        if self.current_account is None:
            return
        index = self._find_account_index(self.current_account.account)
        record = self.current_account.to_dict()
        if index is not None:
            self.data[index] = record
        else:
            self.data.append(record)
        save_accounts(self.data)

    def create_account(self):
        name = input("Enter your name: ").strip()
        pin = input("Set a 4-digit PIN: ").strip()
        account_number = generate_account_number(self.data)

        new_account = {
            "name": name,
            "account": account_number,
            "pin": pin,
            "balance": 0,
            "transactions": [],
        }
        self.data.append(new_account)
        save_accounts(self.data)
        print(f"\n✅ Account created successfully! Your account number is {account_number}")
        print("Please remember this number, you'll need it to log in.")

    def login(self):
        account_number = input("Enter your account number: ").strip()
        pin = input("Enter your PIN: ").strip()

        index = self._find_account_index(account_number)
        if index is None:
            print("\n❌ Account not found")
            return

        record = self.data[index]
        if record["pin"] != pin:
            print("\n❌ Incorrect PIN")
            return

        self.current_account = BankAccount(
            record["name"],
            record["account"],
            record["pin"],
            record["balance"],
            record["transactions"],
        )
        print(f"\n✅ Welcome back, {self.current_account.name}!")

    def transfer_money(self):
        if not self._require_login():
            return
        target_number = input("Enter recipient's account number: ").strip()

        if target_number == self.current_account.account:
            print("\n❌ You can't transfer money to your own account")
            return

        target_index = self._find_account_index(target_number)
        if target_index is None:
            print("\n❌ Recipient account not found")
            return

        try:
            amount = float(input("Enter amount to transfer: "))
        except ValueError:
            print("\n❌ Please enter a valid numeric amount")
            return

        if amount <= 0:
            print("\n❌ Invalid amount")
            return
        if amount > self.current_account.balance:
            print("\n❌ Insufficient balance")
            return

        # Deduct from sender
        self.current_account.balance -= amount
        self.current_account.transactions.append(
            f"Transferred ${amount:.2f} to account {target_number}"
        )

        self.data[target_index]["balance"] += amount
        self.data[target_index]["transactions"].append(
            f"Received ${amount:.2f} from account {self.current_account.account}"
        )

        self.save_current_account()
        save_accounts(self.data)
        print(f"\n✅ Successfully transferred ${amount:.2f} to account {target_number}")

    def _require_login(self):
        if self.current_account is None:
            print("\n❌ Please log in first (option 2)")
            return False
        return True

    def show_menu(self):
        print("\n" + "=" * 30)
        print("1. Create Account")
        print("2. Login")
        print("3. Deposit")
        print("4. Withdraw")
        print("5. Check Balance")
        print("6. Show Transactions")
        print("7. Transfer Money")
        print("8. Change PIN")
        print("9. Exit")
        print("=" * 30)

    def run(self):
        while True:
            try:
                self.show_menu()
                choice = input("Enter your option (1-9): ").strip()

                if choice == "1":
                    self.create_account()

                elif choice == "2":
                    self.login()

                elif choice == "3":
                    if not self._require_login():
                        continue
                    amount = float(input("Enter deposit amount: "))
                    if self.current_account.deposit(amount):
                        self.save_current_account()

                elif choice == "4":
                    if not self._require_login():
                        continue
                    amount = float(input("Enter withdrawal amount: "))
                    if self.current_account.withdraw(amount):
                        self.save_current_account()

                elif choice == "5":
                    if not self._require_login():
                        continue
                    self.current_account.check_balance()

                elif choice == "6":
                    if not self._require_login():
                        continue
                    self.current_account.show_transactions()

                elif choice == "7":
                    self.transfer_money()

                elif choice == "8":
                    if not self._require_login():
                        continue
                    new_pin = input("Enter new PIN: ").strip()
                    self.current_account.change_pin(new_pin)
                    self.save_current_account()

                elif choice == "9":
                    print("👏 Thank you for using the Banking System")
                    break

                else:
                    print("\n❌ Invalid choice. Please try again.")

            except ValueError:
                print("❌ Please enter a valid numeric value.")


if __name__ == "__main__":
    app = BankingApp()
    app.run()