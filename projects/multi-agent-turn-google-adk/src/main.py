"""Main entry point for the application."""

import os
from braintrust import init_logger

# Initialize Braintrust logger
logger = init_logger(project="$PROJECT_NAME")


def main():
    """Main function."""
    print("Hello from $PROJECT_NAME!")
    logger.log(message="Application started")


if __name__ == "__main__":
    main()
