from ultimate_job_bot import UltimateJobBot
from turing_job_bot import TuringJobBot

class ComprehensiveJobBot:
    def __init__(self):
        self.ultimate_bot = UltimateJobBot()
        self.turing_bot = TuringJobBot()

    def run_full_cycle(self):
        """Run full job application cycle across all integrated platforms"""
        print("\n🚀 Running full comprehensive job cycle...")

        # Run ultimate bot cycle (X, RemoteOK, DICE, Indeed, WeWorkRemotely)
        self.ultimate_bot.run_ultimate_cycle()

        # Run Turing bot (for remote developer jobs)
        self.turing_bot.run()

if __name__ == "__main__":
    bot = ComprehensiveJobBot()
    bot.run_full_cycle()
