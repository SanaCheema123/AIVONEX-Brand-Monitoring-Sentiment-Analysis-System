#!/usr/bin/env python3
"""
AIVONEX – Brand Monitoring System
Launcher — starts API and/or Dashboard
"""

import subprocess, sys, os, argparse, signal, time


def run_api():
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "app.main:app", "--host", "0.0.0.0", "--port", "8000",
        "--reload", "--reload-dir", "app"
    ])


def run_dashboard():
    print("🖥️  Starting Streamlit dashboard on http://localhost:8501")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        "dashboard/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--theme.base", "dark",
        "--theme.primaryColor", "#00FF88",
        "--theme.backgroundColor", "#07070F",
        "--theme.secondaryBackgroundColor", "#111118",
        "--theme.textColor", "#E0E0E0",
        "--browser.gatherUsageStats", "false",
    ])


def main():
    parser = argparse.ArgumentParser(description="AIVONEX Brand Monitoring System")
    parser.add_argument("--api-only",       action="store_true", help="Run API server only")
    parser.add_argument("--dashboard-only", action="store_true", help="Run dashboard only")
    args = parser.parse_args()

    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    print("""
╔══════════════════════════════════════════════════════╗
║   AIVONEX – Brand Monitoring & Sentiment System      ║
║   Managed Data Intelligence & AI/ML Services         ║
╚══════════════════════════════════════════════════════╝
    """)

    procs = []
    try:
        if args.api_only:
            procs.append(run_api())
        elif args.dashboard_only:
            procs.append(run_dashboard())
        else:
            procs.append(run_api())
            time.sleep(2)
            procs.append(run_dashboard())
            print("\n✅ Both services started!")
            print("   API:        http://localhost:8000")
            print("   API Docs:   http://localhost:8000/docs")
            print("   Dashboard:  http://localhost:8501")
            print("\nPress Ctrl+C to stop all services.\n")

        for p in procs:
            p.wait()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for p in procs:
            p.terminate()
        print("✅ All services stopped.")


if __name__ == "__main__":
    main()
