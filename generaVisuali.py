import os
import re
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from rembg import remove

# Forza rembg a usare la CPU ed evita i warning di ONNX Runtime
os.environ["ONNXRUNTIME_EXECUTION_PROVIDERS"] = "['CPUExecutionProvider']"


def clean_folder_name(text):
    """Trasforma qualsiasi query in un nome di cartella valido per Windows/Linux"""
    clean = re.sub(r'[^\w\s-]', '', str(text)).strip().lower()
    return re.sub(r'[-\s]+', '_', clean)


def get_text_size(draw, text, font):
    """Calcola le dimensioni del testo in modo sicuro"""
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


def genera_titolo_procedurale(etichetta_pulita, fascia_prezzo):
    """Genera proceduralmente il testo della copertina con la prima lettera maiuscola."""
    etichetta = etichetta_pulita.strip()
    if fascia_prezzo.lower() == "low cost":
        frase = f"{etichetta} lowcost su Amazon che svoltano qualsiasi outfit"
    else:
        frase = f"{etichetta} su Amazon che svoltano qualsiasi outfit"
    return frase[0].upper() + frase[1:]


def create_cover_slide(etichetta_pulita, price_tier, output_path, font_cover, input_bg="sfondo_copertina.jpg"):
    """Crea la slide di copertina (Slide 0) con scritta grande Bordeaux ed alone chiaro."""
    slide_width, slide_height = 1080, 1920

    if os.path.exists(input_bg):
        try:
            cover = Image.open(input_bg).convert("RGBA")
            if cover.size != (slide_width, slide_height):
                cover = cover.resize((slide_width, slide_height), Image.Resampling.LANCZOS)

            # Sfondo sbiadito e morbido
            cover = ImageEnhance.Brightness(cover).enhance(1.10)
            cover = ImageEnhance.Contrast(cover).enhance(0.92)
            overlay = Image.new("RGBA", (slide_width, slide_height), (255, 255, 255, 35))
            slide = Image.alpha_composite(cover, overlay)
        except Exception:
            slide = Image.new("RGBA", (slide_width, slide_height), (239, 233, 223, 255))
    else:
        slide = Image.new("RGBA", (slide_width, slide_height), (239, 233, 223, 255))

    draw = ImageDraw.Draw(slide)
    testo_principale = genera_titolo_procedurale(etichetta_pulita, price_tier)

    # 🍷 Colore Bordeaux elegante e profondo con alone chiaro
    text_color = (78, 28, 38)
    shadow_color = (255, 255, 255, 230)

    margin = 80
    max_width = slide_width - (margin * 2)
    words = testo_principale.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        lw, _ = get_text_size(draw, test_line, font_cover)
        if lw <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    sample_bbox = draw.textbbox((0, 0), "Hg", font=font_cover)
    line_height = (sample_bbox[3] - sample_bbox[1]) + 20
    total_text_height = (len(lines) * line_height) - 20
    y_start = (slide_height - total_text_height) // 2

    for idx, line in enumerate(lines):
        lw, lh = get_text_size(draw, line, font_cover)
        lx = (slide_width - lw) // 2
        ly = y_start + (idx * line_height)

        # Alone circolare per staccare il testo dallo sfondo
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-3, -3), (3, 3), (-2, 2), (2, -2)]:
            draw.text((lx + dx, ly + dy), line, font=font_cover, fill=shadow_color)

        draw.text((lx, ly), line, font=font_cover, fill=text_color)

    slide.convert("RGB").save(output_path, "PNG")
    print(f"✨ Copertina creata -> {output_path}")


def create_tiktok_slides(csv_input="tiktok_ready_posts.csv", base_output_dir="tiktok_slides"):
    if not os.path.exists(csv_input):
        print(f"❌ Errore: Il file {csv_input} non esiste.")
        return

    df = pd.read_csv(csv_input)
    print("🎨 Generazione copertine e slide prodotto in corso...\n")

    # Ricerca dei font (TikTok Sans o fallback)
    font_title, font_quote, font_rating, font_price, font_cover = None, None, None, None, None
    font_families = [
        "TikTokSans-Bold.ttf", "TikTokSans.ttf", "tiktok_sans.ttf",
        "C:\\Windows\\Fonts\\segoeb.ttf", "C:\\Windows\\Fonts\\arialbd.ttf", "arial.ttf"
    ]

    for path in font_families:
        try:
            font_title = ImageFont.truetype(path, 85)
            font_quote = ImageFont.truetype(path, 46)
            font_rating = ImageFont.truetype(path, 40)
            font_price = ImageFont.truetype(path, 80)
            font_cover = ImageFont.truetype(path, 110)
            print(f"✨ Font applicato con successo: {path}")
            break
        except Exception:
            continue

    if font_title is None:
        font_title = font_quote = font_rating = font_price = font_cover = ImageFont.load_default()

    grouped = df.groupby(["Categoria", "Fascia Prezzo"])

    for (category, price_tier), group_df in grouped:
        # ✂️ Limita rigorosamente a massimo 5 elementi per evitare caroselli troppo lunghi
        group_df = group_df.head(5)

        cat_folder = clean_folder_name(category)
        tier_folder = clean_folder_name(price_tier)
        target_dir = os.path.join(base_output_dir, cat_folder, tier_folder)
        os.makedirs(target_dir, exist_ok=True)

        clean_label = str(group_df.iloc[0].get("Etichetta Pulita", category))

        # 1. Genera la Copertina (Slide 0) procedurale
        cover_filename = os.path.join(target_dir, "slide_0_copertina.png")
        create_cover_slide(clean_label, price_tier, cover_filename, font_cover)

        # 2. Genera le 5 slide prodotto successive
        for idx, (_, row) in enumerate(group_df.iterrows(), start=1):
            prod_id = row['ID']
            clean_title = str(row.get('Prodotto', 'FASHION ITEM')).upper()
            raw_price = str(row['Prezzo']).replace("€", "").replace("\n", "").replace(" ", "").strip()
            raw_price = raw_price.replace(",,", ",").replace("..", ".")
            rating = str(row.get('rating', '4,3 su 5 stelle'))
            quote_text = str(row.get('Recensione Top', 'Super comodo!'))

            # Legge direttamente il percorso corretto (es. temp_images/temp_img_ASIN.jpg) salvato nel CSV
            img_path = str(row.get('Immagine Originale', ''))

            if not os.path.exists(img_path):
                print(f"⚠️ Immagine non trovata: {img_path}")
                continue

            try:
                input_image = Image.open(img_path).convert("RGBA")
                output_image = remove(input_image)
                bbox = output_image.getbbox()
                if bbox:
                    output_image = output_image.crop(bbox)

                slide_width, slide_height = 1080, 1920
                slide = Image.new("RGBA", (slide_width, slide_height), (239, 233, 223, 255))

                target_width = 780
                w_percent = target_width / float(output_image.size[0])
                target_height = int((float(output_image.size[1]) * float(w_percent)))

                if target_height > 900:
                    target_height = 900
                    h_percent = target_height / float(output_image.size[1])
                    target_width = int((float(output_image.size[0]) * float(h_percent)))

                output_image = output_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                pos_x = (slide_width - target_width) // 2
                pos_y = 560 + (900 - target_height) // 2  # 🛠️ Sintassi corretta ripristinata

                slide.paste(output_image, (pos_x, pos_y), output_image)

                draw = ImageDraw.Draw(slide)
                text_color_main = (52, 40, 31)
                text_color_sub = (95, 78, 65)

                bbox_brand = draw.textbbox((0, 0), clean_title, font=font_title)
                brand_w = bbox_brand[2] - bbox_brand[0]
                brand_x = (slide_width - brand_w) // 2
                draw.text((brand_x, 100), clean_title, fill=text_color_main, font=font_title)

                bbox_quote = draw.textbbox((0, 0), quote_text, font=font_quote)
                quote_w = bbox_quote[2] - bbox_quote[0]
                quote_x = (slide_width - quote_w) // 2
                draw.text((quote_x, 210), quote_text, fill=text_color_sub, font=font_quote)

                clean_rating = rating.replace("su", "/")
                rating_text = f"Valutazione Amazon: {clean_rating}"
                bbox_rate = draw.textbbox((0, 0), rating_text, font=font_rating)
                rate_w = bbox_rate[2] - bbox_rate[0]
                rate_x = (slide_width - rate_w) // 2
                draw.text((rate_x, 275), rating_text, fill=text_color_sub, font=font_rating)

                price_text = f"solo {raw_price}€"
                bbox_price = draw.textbbox((0, 0), price_text, font=font_price)
                price_w = bbox_price[2] - bbox_price[0]
                price_x = (slide_width - price_w) // 2
                draw.text((price_x, 1590), price_text, fill=text_color_main, font=font_price)

                slide_filename = os.path.join(target_dir, f"slide_{idx}_{prod_id}.png")
                slide.convert("RGB").save(slide_filename, "PNG")
                print(f"✅ Salvato -> {cat_folder}/{tier_folder}/slide_{idx}_{prod_id}.png")

            except Exception as e:
                print(f"❌ Errore nella slide #{prod_id}: {e}")

    print("\n🚀 Generazione di tutte le copertine e le slide completata con successo!")


if __name__ == "__main__":
    create_tiktok_slides()