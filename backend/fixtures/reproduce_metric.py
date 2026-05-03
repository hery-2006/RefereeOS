import csv
import sys


def f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "results.csv"
    scores = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            scores.append(f1(float(row["precision"]), float(row["recall"])))

    if not scores:
        print("macro_f1=0.00")
        return 1

    macro_f1 = sum(scores) / len(scores)
    print(f"macro_f1={macro_f1:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
