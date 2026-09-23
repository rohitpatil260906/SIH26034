import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "sample_test_products")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_label_image(
    filename: str,
    lines: list,
    is_blurred: bool = False,
    bg_color=(250, 250, 248),
    text_color=(20, 25, 30)
):
    width, height = 800, 600
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(180, 180, 180), width=2)
    # Header ribbon
    draw.rectangle([(22, 22), (width - 22, 80)], fill=(235, 235, 240))
    draw.text((40, 40), "LEGAL METROLOGY TEST SAMPLE PACKAGING", fill=(80, 80, 100))

    y_cursor = 100
    for line in lines:
        draw.text((50, y_cursor), line, fill=text_color)
        y_cursor += 45

    if is_blurred:
        # Apply motion/gaussian blur to simulate out-of-focus capture
        img = img.filter(ImageFilter.GaussianBlur(radius=6))

    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "PNG")
    print(f"Generated test sample: {filepath}")
    return filepath

def generate_all_samples():
    # 1. Fully Compliant Label
    create_label_image(
        "sample_1_fully_compliant.png",
        [
            "LAKME SUN EXPERT ULTRA MATTE GEL SPF 50",
            "Net Qty: 50 g",
            "MRP: Rs. 499.00 (inclusive of all taxes)",
            "USP: Rs. 9.98 / g",
            "Mfd: 08/2024 • Exp: 08/2026",
            "Batch: B-LK8942",
            "Mfd by: Aero Care Personal Products, Survey 284/2, Naroli 396235, D&NH",
            "Consumer Care: 1800-10-22-221 • care@unilever.com",
            "Country of Origin: India"
        ]
    )

    # 2. Missing MRP Declaration (Violation under Rule 6(1)(e))
    create_label_image(
        "sample_2_missing_mrp.png",
        [
            "HERITAGE KACHI GHANI MUSTARD OIL",
            "Net Qty: 1 L",
            "Mfd: 05/2024 • Best Before 12 Months",
            "Batch: HR-7712",
            "Mfd by: Heritage Agro Ltd, Industrial Area, Rewari 123401, Haryana",
            "Consumer Helpline: 1800-200-4411",
            "Country of Origin: India"
            # Note: No MRP line included
        ]
    )

    # 3. Missing Manufacturer & Postal PIN code (Violation under Rule 6(1)(a) & Rule 10)
    create_label_image(
        "sample_3_missing_manufacturer_pin.png",
        [
            "SWACHH BHARAT ADVANCED DETERGENT",
            "Net Qty: 1 kg",
            "MRP: Rs. 140.00 (inclusive of all taxes)",
            "Mfd: 02/2025",
            "Batch: SB-902",
            "Packed by: CleanHome India Ltd, Industrial Estate", # Missing 6-digit PIN & state
            "Helpline: 011-23849102",
            "Country of Origin: India"
        ]
    )

    # 4. Missing Consumer Care Information (Violation under Rule 6(1)(f))
    create_label_image(
        "sample_4_missing_consumer_care.png",
        [
            "GOLDEN HARVEST PREMIUM BASMATI RICE",
            "Net Qty: 5 kg",
            "MRP: Rs. 550.00 (inclusive of all taxes)",
            "Mfd: 01/2025",
            "Batch: GH-110",
            "Packed by: Golden Agro Foods, Plot 8, Karnal 132001, Haryana",
            "Country of Origin: India"
            # Note: No consumer care helpline / email
        ]
    )

    # 5. Poor Quality / Blurry Image (Triggers REVIEW under Quality Gate)
    create_label_image(
        "sample_5_blurry_degraded.png",
        [
            "DEGRADED PACKAGING SPECIMEN",
            "Net Qty: 200 g",
            "MRP: Rs. 99.00 (incl. of all taxes)",
            "Mfd: 04/2024",
            "Consumer Care: 1800-44-55-66"
        ],
        is_blurred=True
    )

    # 6. Prohibited Non-Standard Metric Unit (Violation under Rule 13: 'gms' instead of 'g')
    create_label_image(
        "sample_6_prohibited_unit_gms.png",
        [
            "NUTRI-CRUNCH HERBAL DIGESTIVE BISCUITS",
            "Net Content: 250 gms",  # Violation: non-SI unit 'gms'
            "MRP: Rs. 60.00 (inclusive of all taxes)",
            "Mfd: 06/2024",
            "Batch: NC-88",
            "Mfd by: NutriBake Foods Ltd, Sector 4, Haridwar 249403, Uttarakhand",
            "Consumer Cell: 1800-33-44-55",
            "Country of Origin: India"
        ]
    )

if __name__ == "__main__":
    generate_all_samples()
