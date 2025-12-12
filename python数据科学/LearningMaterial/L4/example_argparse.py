import argparse
# import sys

# Create parser
parser = argparse.ArgumentParser(description="Simple Weather Analyzer")

# Add arguments
parser.add_argument("--input", "-i", required=True, help="Input data file")
parser.add_argument("--output", "-o", default="results.txt", help="Output results file")
parser.add_argument("--threshold", "-t", type=float, default=0.5, help="Threshold for alerts")

# Parse
if __name__ == "__main__":
    # In a Jupyter notebook, emulate sys.argv:
    # sys.argv = ["analyze.py", "--input", "weather_data.csv", "--threshold", "1.0"]
    
    args = parser.parse_args()
    print(f"Analyzing {args.input}")
    print(f"Threshold: {args.threshold}")
    print(f"Results will be saved to: {args.output}")
