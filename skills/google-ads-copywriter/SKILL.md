---
name: google-ads-copywriter
description: Viết mẫu quảng cáo Google Ads Search (RSA) — headline, description, extension — cho một nhóm từ khóa/dịch vụ/khu vực/khuyến mãi cụ thể.
---

# Skill: Google Ads Copywriter

## Khi nào dùng skill này

Dùng skill này khi cần **viết mới hoặc làm mới nội dung quảng cáo Google Ads
Search (Responsive Search Ads - RSA)** cho một nhóm quảng cáo (ad group) cụ
thể — ví dụ: ra mắt campaign mới, thêm ad group mới, thay khuyến mãi theo
mùa, hoặc cải thiện Ad Strength.

Không dùng skill này cho Display, Performance Max, Shopping hay Social Ads —
skill này chỉ tập trung vào Search RSA.

## Input cần hỏi người dùng

Trước khi viết, luôn xác nhận đủ các thông tin sau (nếu người dùng chưa cung
cấp, hỏi lại — không tự bịa):

1. **Sản phẩm/dịch vụ** — tên cụ thể, không chung chung.
2. **Bộ từ khóa** — danh sách từ khóa chính của ad group này.
3. **Khu vực chạy quảng cáo** — thành phố/tỉnh/quốc gia.
4. **Đối tượng mục tiêu** — ai sẽ thấy quảng cáo (B2B/B2C, độ tuổi, nhu cầu).
5. **USP (Unique Selling Point)** — điểm khác biệt cụ thể, có thể chứng minh
   được (ví dụ: "bảo hành 24 tháng", "giao trong 2h", chứ không phải "tốt
   nhất thị trường").
6. **Chương trình khuyến mãi** — nếu có, ghi rõ điều kiện/thời hạn.
7. **Tone of voice** — chuyên nghiệp, thân thiện, khẩn cấp, sang trọng, v.v.

## Output

1. **15 headlines**, mỗi headline **tối đa 30 ký tự** (tính cả dấu cách và
   dấu câu).
2. **4 descriptions**, mỗi description **tối đa 90 ký tự**.
3. Headline viết hoa chữ cái đầu mỗi từ (Title Case), trừ các từ nối ngắn
   (và, của, cho) nếu không đứng đầu.
4. Bảng **kiểm tra độ dài ký tự** cho từng headline/description (đếm ký tự
   thực tế, đánh dấu ✅/❌ nếu vượt giới hạn).
5. Gợi ý **sitelink, callout, structured snippet** nếu phù hợp với dịch vụ
   (tham khảo `templates/extension_templates.md`).

Trình bày output theo bảng, nhóm rõ Headlines / Descriptions / Extensions để
dễ copy-paste vào Google Ads Editor.

## Quy tắc viết

- **Ưu tiên keyword chính trong headline** — ít nhất 5/15 headline phải chứa
  từ khóa chính hoặc biến thể gần đúng.
- **Có CTA rõ ràng** trong ít nhất 3 headline và tất cả description (Gọi Ngay,
  Đăng Ký, Nhận Báo Giá, Tư Vấn Miễn Phí...).
- **Có USP cụ thể** — mỗi USP phải là thứ có thể chứng minh, tránh superlative
  mơ hồ ("số 1", "tốt nhất") trừ khi người dùng xác nhận có bằng chứng
  (giải thưởng, số liệu, chứng nhận).
- **Không claim quá đà nếu chưa có bằng chứng.** Nếu người dùng đưa USP dạng
  claim tuyệt đối mà không có số liệu/chứng nhận đi kèm, phải hỏi lại hoặc
  đề xuất diễn đạt an toàn hơn.
- **Nếu bộ từ khóa lệch nhóm** (ví dụ trộn lẫn "thiết kế nội thất phòng ngủ"
  với "sửa chữa điện nước"), **phải cảnh báo người dùng** rằng nên tách thành
  nhiều ad group riêng để giữ độ liên quan (Quality Score) cao, và hỏi xem có
  muốn tách trước khi viết tiếp không.
- Dùng các công thức trong `templates/rsa_headline_templates.md` và
  `templates/rsa_description_templates.md` làm khung, không copy nguyên văn
  mà điều chỉnh theo input thực tế.

## Ví dụ

Xem ví dụ hoàn chỉnh cho ngành nội thất tại
`examples/bedroom_interior_ads_example.md`.

## Tài nguyên đi kèm

- `templates/rsa_headline_templates.md` — công thức headline theo nhóm mục
  đích (keyword, USP, CTA, khuyến mãi, khu vực, câu hỏi, số liệu).
- `templates/rsa_description_templates.md` — công thức description (mở đầu,
  USP + proof, CTA + urgency).
- `templates/extension_templates.md` — mẫu sitelink/callout/structured
  snippet theo ngành phổ biến.
- `examples/bedroom_interior_ads_example.md` — ví dụ đầy đủ input → output
  cho dịch vụ thiết kế thi công phòng ngủ.
