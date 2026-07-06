---
name: search-terms-negative-keyword
description: Phân tích file Search Terms export từ Google Ads (qua CLI script Python) và gợi ý bộ từ khóa phủ định theo cấp độ và mức độ lọc.
---

# Skill: Search Terms & Negative Keyword Analyzer

## Khi nào dùng skill này

Dùng skill này khi người dùng có **file Search Terms Report export từ Google
Ads** (CSV) và muốn tìm ra các cụm từ tìm kiếm đang gây lãng phí ngân sách để
đưa vào danh sách **từ khóa phủ định (negative keywords)**.

Đây là skill **kết nối với công cụ ngoài qua CLI**: dữ liệu gốc đến từ nền
tảng Google Ads (export thủ công thành CSV), và việc xử lý được thực hiện
bằng cách **chạy script Python từ dòng lệnh**
(`scripts/negative_keyword_analyzer.py`) — không cần API key, không cần kết
nối mạng.

## Cách sử dụng CLI script

1. Xác định file CSV search terms (dùng file thật của khách hàng, hoặc dùng
   sample có sẵn tại `data/sample_search_terms.csv` để test).
2. Chạy lệnh:

```bash
python skills/search-terms-negative-keyword/scripts/negative_keyword_analyzer.py \
  --input skills/search-terms-negative-keyword/data/sample_search_terms.csv \
  --output skills/search-terms-negative-keyword/output/negative_keywords.csv \
  --product "tour trung quốc" \
  --level campaign \
  --mode balanced
```

3. Mở file output CSV để xem danh sách từ khóa phủ định đề xuất, hoặc yêu
   cầu Claude đọc và tóm tắt file output thành bảng dễ đọc + khuyến nghị hành
   động tiếp theo.

Claude có thể tự chạy script này bằng Bash tool nếu người dùng yêu cầu, thay
vì tự đọc/phân tích CSV thủ công trong context — script đảm bảo tính nhất
quán và có thể tái sử dụng cho các file search terms khác.

## Input

1. **File search terms CSV** (bắt buộc) — export từ Google Ads.
2. **Sản phẩm/dịch vụ đang quảng cáo** (bắt buộc) — dùng để phát hiện search
   term lệch sản phẩm/quốc gia (`--product`).
3. **Từ khóa chính cần giữ** (tùy chọn) — danh sách để đối chiếu, tránh đề
   xuất phủ định trùng ý với keyword đang target (`--keep`).
4. **Từ khóa không được phủ định** (tùy chọn) — whitelist bảo vệ, dù có
   match rule cũng bỏ qua (`--protect`).
5. **Cấp phủ định mong muốn** — `account`, `campaign`, `ad_group`, hoặc
   `cross_negative` (`--level`, mặc định `campaign`).
6. **Mức độ lọc** — `safe`, `balanced`, hoặc `aggressive` (`--mode`, mặc định
   `balanced`).

## Output

File CSV với các cột:

| Cột | Ý nghĩa |
|---|---|
| `negative_keyword` | Từ/cụm từ đề xuất phủ định |
| `match_type` | `negative exact`, `negative phrase`, hoặc `negative broad` |
| `negative_level` | Cấp áp dụng: account/campaign/ad_group/cross_negative |
| `reason` | Lý do phủ định (nhóm rule nào phát hiện) |
| `confidence` | High / Medium / Low |
| `source_search_term` | Cụm từ tìm kiếm gốc |
| `campaign` | Campaign chứa search term này |
| `ad_group` | Ad group chứa search term này |
| `clicks`, `cost`, `conversions` | Chỉ số gốc để đánh giá mức độ lãng phí |

Khi tóm tắt kết quả cho người dùng, luôn nhóm theo `confidence` (High trước)
và nêu rõ **tổng cost đã lãng phí** vào các search term High confidence, để
người dùng ưu tiên xử lý trước.

## Các nhóm rule nhận diện từ khóa phủ định

Script nhận diện các nhóm sau (dựa trên từ khóa/pattern tiếng Việt phổ biến):

1. **Tuyển dụng/việc làm** — "tuyển dụng", "việc làm", "tuyển nhân viên"...
2. **Du học/học tập** — "du học", "học bổng", "học tiếng"...
3. **Miễn phí/download/crack** — "miễn phí", "download", "crack", "torrent"...
4. **Tự túc/DIY** — "tự túc", "tự làm", "hướng dẫn tự"...
5. **Tin tức/thời tiết/bản đồ** — "tin tức", "thời tiết", "bản đồ", "wikipedia"...
6. **Phim/nhạc/giải trí** — "phim", "nhạc", "trailer", "review phim"...
7. **Sai quốc gia/sai sản phẩm** — search term chứa tên quốc gia/sản phẩm
   khác với `--product` đã khai báo (ví dụ product là "tour trung quốc" mà
   search term chứa "tour hàn quốc").
8. **Search intent thấp** — "là gì", "giá bao nhiêu" (không kèm intent mua),
   "review", "so sánh" khi không có conversion.

## Quy tắc theo mức độ lọc (`--mode`)

- **safe**: Chỉ đề xuất phủ định các search term khớp rule rõ ràng (nhóm
  1-6) và có ít nhất 1 click nhưng 0 conversion. Confidence chủ yếu High/Medium.
- **balanced** (mặc định): Thêm rule sai quốc gia/sản phẩm (nhóm 7) và xét cả
  search term chưa có click nhưng có impression cao bất thường.
- **aggressive**: Thêm rule search intent thấp (nhóm 8), hạ ngưỡng conversion
  cần thiết, đề xuất phủ định cả các search term nghi ngờ dù confidence Low.
  Luôn cảnh báo người dùng review kỹ trước khi áp dụng ở mode này.

## Lưu ý khi trình bày kết quả

- Luôn liệt kê rõ danh sách trong `--protect` đã được loại trừ khỏi đề xuất.
- Nếu `--level` là `account`, nhắc người dùng cẩn trọng vì phủ định ở cấp
  account ảnh hưởng toàn bộ campaign khác.
- Nếu `--level` là `cross_negative`, giải thích đây là dùng để tách traffic
  giữa 2 campaign tương tự nhau (ví dụ Brand vs Non-Brand), không phải để
  chặn traffic xấu.
