from flask import Flask, render_template, request, send_file
from itertools import combinations
from io import BytesIO
import csv

app = Flask(__name__)

TRANSACTIONS = {
    "Paket 1": ["BARCELONA", "MADRID", "LISBON", "PORTO", "PARIS", "LONDON"],
    "Paket 2": ["BERN", "PARIS", "BRUSSEL", "AMSTERDAM", "ROTTERDAM", "BERLIN"],
    "Paket 3": ["PARIS", "BERN", "MONACO", "MILAN", "ROMA", "ATHENA", "ISTANBUL"],
    "Paket 4": ["LISBON", "MADRID", "PARIS", "BERN", "WIENA", "ZAGREB", "BUCHAREST"],
    "Paket 5": ["PARIS", "BRUSSEL", "LONDON", "MANCHESTER", "EDINBURGH", "REYKJAVIK"],
    "Paket 6": ["BARCELONA", "MADRID", "PARIS", "BERN", "MILAN", "ROMA", "ATHENA"],
    "Paket 7": ["ISTANBUL", "ATHENA", "ROMA", "MILAN", "BERN", "PARIS", "BRUSSEL", "BERLIN"],
    "Paket 8": ["MADRID", "LISBON", "DUBLIN", "LONDON", "AMSTERDAM", "BERLIN"],
}

def apriori(transactions, min_support, min_confidence):
    """Menghasilkan seluruh level kandidat/frequent itemset dan association rule."""
    total = len(transactions)
    min_count = max(1, int((min_support * total) - 1e-12 + 0.999999999))
    baskets = [set(items) for items in transactions.values()]
    levels = []
    rules = []

    # C1
    all_items = sorted(set().union(*baskets))
    candidates = [(item,) for item in all_items]

    k = 1
    while candidates:
        candidate_counts = {}
        for candidate in candidates:
            candidate_set = set(candidate)
            candidate_counts[candidate] = sum(candidate_set.issubset(basket) for basket in baskets)

        frequent = {itemset: count for itemset, count in candidate_counts.items()
                    if count >= min_count}

        levels.append({
            "k": k,
            "candidates": [
                {"items": list(itemset), "count": count, "support": count / total,
                 "frequent": count >= min_count}
                for itemset, count in sorted(candidate_counts.items())
            ],
            "frequent": [
                {"items": list(itemset), "count": count, "support": count / total}
                for itemset, count in sorted(frequent.items())
            ]
        })

        if not frequent:
            break

        # Generate association rules from every frequent itemset of size >= 2.
        for itemset, union_count in frequent.items():
            if len(itemset) < 2:
                continue
            itemset_set = set(itemset)
            for size in range(1, len(itemset)):
                for antecedent_tuple in combinations(itemset, size):
                    antecedent = tuple(sorted(antecedent_tuple))
                    consequent = tuple(sorted(itemset_set - set(antecedent)))
                    antecedent_count = sum(set(antecedent).issubset(b) for b in baskets)
                    if antecedent_count:
                        confidence = union_count / antecedent_count
                        if confidence + 1e-12 >= min_confidence:
                            rules.append({
                                "antecedent": list(antecedent),
                                "consequent": list(consequent),
                                "support": union_count / total,
                                "confidence": confidence,
                                "count": union_count
                            })

        # Apriori join and prune: all (k)-subsets must be frequent.
        frequent_sets = set(frequent.keys())
        next_candidates = set()
        frequent_sorted = sorted(frequent_sets)
        for i in range(len(frequent_sorted)):
            for j in range(i + 1, len(frequent_sorted)):
                left, right = frequent_sorted[i], frequent_sorted[j]
                if left[:k-1] == right[:k-1]:
                    candidate = tuple(sorted(set(left) | set(right)))
                    if len(candidate) == k + 1:
                        subsets = combinations(candidate, k)
                        if all(tuple(sorted(sub)) in frequent_sets for sub in subsets):
                            next_candidates.add(candidate)
        candidates = sorted(next_candidates)
        k += 1

    # Remove duplicate rules defensively and sort by confidence, support, then names.
    unique = {}
    for rule in rules:
        key = (tuple(rule["antecedent"]), tuple(rule["consequent"]))
        unique[key] = rule
    rules = sorted(unique.values(),
                   key=lambda r: (-r["confidence"], -r["support"],
                                  r["antecedent"], r["consequent"]))
    return levels, rules, min_count

@app.route("/", methods=["GET", "POST"])
def index():
    min_support = 0.30
    min_confidence = 0.80
    analyzed = False
    levels, rules, min_count = [], [], 0
    error = None

    if request.method == "POST":
        try:
            min_support = float(request.form.get("min_support", "30")) / 100
            min_confidence = float(request.form.get("min_confidence", "80")) / 100
            if not (0 < min_support <= 1 and 0 < min_confidence <= 1):
                raise ValueError("Nilai support dan confidence harus lebih dari 0 dan maksimal 1.")
            levels, rules, min_count = apriori(TRANSACTIONS, min_support, min_confidence)
            analyzed = True
        except ValueError as exc:
            error = str(exc)

    unique_cities = sorted(set(city for items in TRANSACTIONS.values() for city in items))
    frequent_count = sum(len(level["frequent"]) for level in levels)
    return render_template(
        "index.html",
        transactions=TRANSACTIONS,
        city_count=len(unique_cities),
        unique_cities=unique_cities,
        min_support=min_support,
        min_confidence=min_confidence,
        analyzed=analyzed,
        levels=levels,
        rules=rules,
        min_count=min_count,
        frequent_count=frequent_count,
        error=error
    )

@app.route("/export")
def export_csv():
    support = float(request.args.get("support", "0.30"))
    confidence = float(request.args.get("confidence", "0.80"))
    if not (0 < support <= 1 and 0 < confidence <= 1):
        return "Parameter tidak valid", 400
    levels, rules, min_count = apriori(TRANSACTIONS, support, confidence)
    output = BytesIO()
    # CSV UTF-8 with BOM for Excel compatibility
    import io
    text_buffer = io.StringIO()
    writer = csv.writer(text_buffer)
    writer.writerow(["Jenis", "Itemset / Aturan", "Jumlah", "Support", "Confidence"])
    for level in levels:
        for row in level["frequent"]:
            writer.writerow([f"L{level['k']}", " + ".join(row["items"]), row["count"],
                             f"{row['support']:.4f}", ""])
    for rule in rules:
        writer.writerow(["Association Rule",
                         " + ".join(rule["antecedent"]) + " -> " + " + ".join(rule["consequent"]),
                         rule["count"], f"{rule['support']:.4f}", f"{rule['confidence']:.4f}"])
    output.write(("\ufeff" + text_buffer.getvalue()).encode("utf-8"))
    output.seek(0)
    return send_file(output, mimetype="text/csv", as_attachment=True,
                     download_name="hasil_apriori_unsrat.csv")

if __name__ == "__main__":
    app.run(debug=True)
