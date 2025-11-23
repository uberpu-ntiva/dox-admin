#!/usr/bin/env python3
"""
Jules Local Watcher (MCP Bridge)
================================

This script acts as the local "watcher" for the Jules MCP workflow.
It bridges the gap between the file-based signals from Jules (the agent)
and the autonomous commit system.

Protocol:
1. Jules (Agent) does work.
2. Jules creates 'planning.md' (The RP - Repo Plan).
3. Jules waits for approval (simulated here or external).
4. Jules creates '.jules_ready' signal file.
5. This watcher detects '.jules_ready', verifies 'planning.md', and triggers 'rpa-commit.sh'.

Usage:
    ./scripts/jules_watcher.py [--dry-run] [--interval SECONDS]
"""

import os
import sys
import time
import argparse
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [JULES-MCP] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("JulesWatcher")

# Constants
SIGNAL_FILE = ".jules_ready"
PLAN_FILE = "planning.md"
QNA_FILE = "QNA.md"
COMMITTED_MARKER = ".jules_committed"
RPA_SCRIPT = "scripts/rpa-commit.sh"

def setup_args():
    parser = argparse.ArgumentParser(description="Jules Local Watcher")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without committing")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    return parser.parse_args()

def check_environment():
    """Verify environment and scripts exist"""
    if not os.path.exists(RPA_SCRIPT):
        logger.error(f"RPA script not found: {RPA_SCRIPT}")
        return False

    # Ensure RPA script is executable
    if not os.access(RPA_SCRIPT, os.X_OK):
        logger.warning(f"Making {RPA_SCRIPT} executable...")
        try:
            os.chmod(RPA_SCRIPT, 0o755)
        except Exception as e:
            logger.error(f"Failed to chmod RPA script: {e}")
            return False

    return True

def perform_commit(dry_run=False):
    """Execute the RPA commit workflow"""
    logger.info("Initiating Autonomous Commit Sequence...")

    if dry_run:
        logger.info("[DRY-RUN] Would execute: ./scripts/rpa-commit.sh quick 'Jules Autonomous Commit'")
        return True

    try:
        # We use 'quick' mode for autonomous commits
        # The message indicates it was triggered by the Jules Watcher
        cmd = [RPA_SCRIPT, "quick", "Jules Autonomous Commit (triggered by Watcher)"]

        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        logger.info("Commit successful!")
        logger.info(f"Output:\n{result.stdout}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Commit failed!")
        logger.error(f"Error Output:\n{e.stderr}")
        logger.error(f"Standard Output:\n{e.stdout}")
        return False

def main():
    args = setup_args()

    logger.info("Starting Jules Local Watcher...")
    logger.info(f"Watching for signal: {SIGNAL_FILE}")

    if not check_environment():
        sys.exit(1)

    try:
        while True:
            if os.path.exists(SIGNAL_FILE):
                logger.info(f"Signal detected: {SIGNAL_FILE}")

                # 1. Verify RP (Repo Plan)
                if not os.path.exists(PLAN_FILE):
                    logger.warning(f"Missing {PLAN_FILE} (RP). Proceeding with caution, but RP is recommended.")
                else:
                    logger.info(f"Verified existence of {PLAN_FILE}")

                # 2. Check for Q&A (Optional)
                if os.path.exists(QNA_FILE):
                    logger.info(f"Found {QNA_FILE}. Assuming questions resolved if signal is present.")

                # 3. Perform Commit
                success = perform_commit(dry_run=args.dry_run)

                if success:
                    # 4. Cleanup and Mark
                    logger.info("Cleaning up signal file...")
                    if not args.dry_run:
                        os.rename(SIGNAL_FILE, COMMITTED_MARKER)
                        logger.info(f"Created marker: {COMMITTED_MARKER}")
                    else:
                        logger.info("[DRY-RUN] Would rename .jules_ready to .jules_committed")
                        # Remove signal in dry run to prevent infinite loop in testing
                        # os.remove(SIGNAL_FILE)
                        # Actually, in dry-run loop, we might want to just sleep longer or exit
                        logger.info("[DRY-RUN] Exiting loop to prevent spam.")
                        break
                else:
                    logger.error("Commit sequence failed. Retaining signal file for retry.")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Watcher stopped by user.")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
