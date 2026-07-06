#!/usr/bin/env python3
"""CLI script: phan tich Search Terms Report (Google Ads) va goi y tu khoa phu dinh.

Chi dung thu vien chuan Python: csv, argparse, re, os.

Vi du chay:
    python negative_keyword_analyzer.py \
        --input ../data/sample_search_terms.csv \
        --output ../output/negative_keywords.csv \
        --product "tour trung quoc" \
        --keep "tour trung quoc,tour bac kinh,tour thuong hai" \
        --level campaign \
        --mode balanced
"""

import argparse
import csv
import os
import re

# ---------------------------------------------------------------------------
# Cau hinh: mapping ten cot (Anh + Viet), danh sach quoc gia, rule nhan dien
# ---------------------------------------------------------------------------

COLUMN_ALIASES = {
    "search_term": ["search term", "cụm từ tìm kiếm", "cum tu tim kiem"],
    "campaign": ["campaign", "chiến dịch", "chien dich"],
    "ad_group": ["ad group", "nhóm quảng cáo", "nhom quang cao"],
    "clicks": ["clicks", "lượt nhấp", "luot nhap"],
    "impressions": ["impressions", "lượt hiển thị", "luot hien thi"],
    "cost": ["cost", "chi phí", "chi phi"],
    "conversions": ["conversions", "chuyển đổi", "chuyen doi"],
}

COUNTRIES = [
    "trung quốc", "hàn quốc", "nhật bản", "thái lan", "singapore",
    "malaysia", "indonesia", "campuchia", "lào", "philippines",
    "đài loan", "hong kong", "úc", "mỹ", "anh", "pháp", "đức", "nga",
    "dubai", "ấn độ",
]

# Thu tu danh gia cac nhom rule "chu de" (khong tinh rule quoc gia va rule intent thap)
TOPIC_RULE_ORDER = [
    "tuyển dụng/việc làm",
    "du học/học tập",
    "miễn phí/download/crack",
    "tự túc/diy",
    "tin tức/thời tiết/bản đồ",
    "phim/nhạc/giải trí",
]

RULE_GROUPS = {
    "tuyển dụng/việc làm": [
        r"\btuyển dụng\b", r"\bviệc làm\b", r"\btuyển nhân viên\b",
    ],
    "du học/học tập": [
        r"\bdu học\b", r"\bhọc bổng\b", r"\bhọc tiếng\b",
    ],
    "miễn phí/download/crack": [
        r"\bmiễn phí\b", r"\bdownload\b", r"\btải về\b", r"\bcrack\b",
        r"\btorrent\b", r"\bpdf\b",
    ],
    "tự túc/diy": [
        r"\btự túc\b", r"\btự đi\b", r"\btự làm\b", r"\bhướng dẫn tự\b",
    ],
    "tin tức/thời tiết/bản đồ": [
        r"\btin tức\b", r"\bthời tiết\b", r"\bbản đồ\b", r"\bwikipedia\b",
    ],
    "phim/nhạc/giải trí": [
        r"\bphim\b", r"\bnhạc\b", r"\btrailer\b", r"\bca sĩ\b",
    ],
    "search intent thấp": [
        r"\blà gì\b", r"\breview\b", r"\bso sánh\b", r"\bgiá bao nhiêu\b",
    ],
}

MATCH_TYPE_BY_GROUP = {
    "tuyển dụng/việc làm": "negative phrase",
    "du học/học tập": "negative phrase",
    "miễn phí/download/crack": "negative phrase",
    "tự túc/diy": "negative phrase",
    "tin tức/thời tiết/bản đồ": "negative phrase",
    "phim/nhạc/giải trí": "negative phrase",
    "sai quốc gia/sai sản phẩm": "negative exact",
    "search intent thấp": "negative broad",
}

REASON_TEMPLATES = {
    "tuyển dụng/việc làm": "Search term liên quan tuyển dụng/việc làm, không phải nhu cầu mua '{product}'.",
    "du học/học tập": "Search term liên quan du học/học tập, không phải nhu cầu mua '{product}'.",
    "miễn phí/download/crack": "Search term tìm nội dung miễn phí/tải về, không phải nhu cầu mua '{product}'.",
    "tự túc/diy": "Search term thể hiện nhu cầu tự làm/tự túc, không cần dịch vụ trọn gói '{product}'.",
    "tin tức/thời tiết/bản đồ": "Search term mang tính tra cứu thông tin (tin tức/thời tiết/bản đồ), không phải nhu cầu mua '{product}'.",
    "phim/nhạc/giải trí": "Search term liên quan phim/nhạc/giải trí, không liên quan '{product}'.",
    "sai quốc gia/sai sản phẩm": "Search term đề cập quốc gia/sản phẩm khác ('{candidate}') so với '{product}' đang quảng cáo.",
    "search intent thấp": "Search term mang tính tìm hiểu chung, chưa rõ intent mua '{product}'.",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_header(header):
    return header.strip().lower()


def build_column_map(fieldnames):
    normalized = {normalize_header(f): f for f in fieldnames}
    mapping = {}
    for key, aliases in COLUMN_ALIASES.items():
        found = None
        for alias in aliases:
            if alias in normalized:
                found = normalized[alias]
                break
        if found is None:
            raise SystemExit(
                "Khong tim thay cot cho '%s'. Cac ten cot hop le: %s"
                % (key, ", ".join(aliases))
            )
        mapping[key] = found
    return mapping


def parse_number(value):
    if value is None:
        return 0.0
    cleaned = re.sub(r"[^\d.\-]", "", str(value))
    if cleaned in ("", "-", "."):
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def detect_product_country(product):
    product_l = product.lower()
    for country in COUNTRIES:
        if country in product_l:
            return country
    return None


def is_protected(candidate, terms):
    candidate_l = candidate.lower().strip()
    for term in terms:
        term_l = term.strip().lower()
        if not term_l:
            continue
        if candidate_l in term_l or term_l in candidate_l:
            return True
    return False


def find_negative_candidate(search_term, product_country, mode):
    text = " " + search_term.lower().strip() + " "

    if mode != "safe" and product_country:
        for country in COUNTRIES:
            if country == product_country:
                continue
            if re.search(r"\b" + re.escape(country) + r"\b", text):
                return "sai quốc gia/sai sản phẩm", country

    for group in TOPIC_RULE_ORDER:
        for pattern in RULE_GROUPS[group]:
            match = re.search(pattern, text)
            if match:
                return group, match.group(0).strip()

    if mode == "aggressive":
        for pattern in RULE_GROUPS["search intent thấp"]:
            match = re.search(pattern, text)
            if match:
                return "search intent thấp", match.group(0).strip()

    return None, None


def determine_confidence(clicks, impressions, conversions):
    if conversions > 0:
        return None
    if clicks > 0:
        return "High"
    if impressions >= 50:
        return "Medium"
    return "Low"


def confidence_allowed(confidence, mode):
    if mode == "safe":
        return confidence == "High"
    if mode == "balanced":
        return confidence in ("High", "Medium")
    return confidence in ("High", "Medium", "Low")  # aggressive


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Phan tich Search Terms Report va goi y tu khoa phu dinh cho Google Ads."
    )
    parser.add_argument("--input", required=True, help="Duong dan file CSV search terms dau vao")
    parser.add_argument("--output", required=True, help="Duong dan file CSV ket qua dau ra")
    parser.add_argument("--product", required=True, help="San pham/dich vu dang quang cao")
    parser.add_argument("--keep", default="", help="Danh sach tu khoa chinh can giu, cach nhau boi dau phay")
    parser.add_argument("--protect", default="", help="Danh sach tu khoa khong duoc phu dinh, cach nhau boi dau phay")
    parser.add_argument(
        "--level", default="campaign",
        choices=["account", "campaign", "ad_group", "cross_negative"],
        help="Cap phu dinh mong muon (mac dinh: campaign)",
    )
    parser.add_argument(
        "--mode", default="balanced",
        choices=["safe", "balanced", "aggressive"],
        help="Muc do loc (mac dinh: balanced)",
    )
    args = parser.parse_args()

    keep_list = [k for k in args.keep.split(",") if k.strip()]
    protect_list = [p for p in args.protect.split(",") if p.strip()]
    product_country = detect_product_country(args.product)

    with open(args.input, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("File input rong hoac khong co header.")
        col = build_column_map(reader.fieldnames)
        rows = list(reader)

    results = []
    total_wasted_cost = 0.0

    for row in rows:
        search_term = (row.get(col["search_term"]) or "").strip()
        if not search_term:
            continue

        campaign = (row.get(col["campaign"]) or "").strip()
        ad_group = (row.get(col["ad_group"]) or "").strip()
        clicks = int(parse_number(row.get(col["clicks"])))
        impressions = int(parse_number(row.get(col["impressions"])))
        cost = parse_number(row.get(col["cost"]))
        conversions = parse_number(row.get(col["conversions"]))

        group, candidate = find_negative_candidate(search_term, product_country, args.mode)
        if not group:
            continue

        confidence = determine_confidence(clicks, impressions, conversions)
        if confidence is None:
            continue  # search term da co conversion, khong phu dinh
        if not confidence_allowed(confidence, args.mode):
            continue

        if is_protected(candidate, protect_list) or is_protected(candidate, keep_list):
            continue

        reason = REASON_TEMPLATES[group].format(product=args.product, candidate=candidate)

        if confidence == "High":
            total_wasted_cost += cost

        results.append({
            "negative_keyword": candidate,
            "match_type": MATCH_TYPE_BY_GROUP[group],
            "negative_level": args.level,
            "reason": reason,
            "confidence": confidence,
            "source_search_term": search_term,
            "campaign": campaign,
            "ad_group": ad_group,
            "clicks": clicks,
            "cost": cost,
            "conversions": conversions,
        })

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = [
        "negative_keyword", "match_type", "negative_level", "reason",
        "confidence", "source_search_term", "campaign", "ad_group",
        "clicks", "cost", "conversions",
    ]
    with open(args.output, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("Da phan tich %d search terms." % len(rows))
    print("De xuat %d tu khoa phu dinh (mode=%s, level=%s)." % (len(results), args.mode, args.level))
    print("Tong chi phi lang phi (confidence=High): %.0f" % total_wasted_cost)
    print("Ket qua da luu tai: %s" % args.output)


if __name__ == "__main__":
    main()
