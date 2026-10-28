import pandas as pd
import os


def detect_category(title):
    """Riconosce la categoria del prodotto dal titolo per adattare l'estetica"""
    title_lower = title.lower()

    categories = {
        "bags": ["borsa", "tracolla", "zaino", "pochette", "shopper", "bag", "valigia"],
        "clothing": ["abito", "vestito", "maglia", "pantalone", "giacca", "cappotto", "gonna", "shirt", "dress",
                     "felpa"],
        "shoes": ["scarpe", "sneakers", "stivali", "tacco", "sandali", "ciabatte"],
        "jewelry": ["orologio", "collana", "anello", "bracciale", "orecchini"]
    }

    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    return "general_fashion"


def get_smart_prompt_and_hook(category, short_title, price, index):
    """Genera hook e prompt calibrati al 100% sulla categoria specifica"""

    if category == "bags":
        hooks = [
            f"La borsa che tutti pensano sia di lusso, ma costa solo {price}€ 🤫",
            f"Ho trovato la borsa perfetta per ogni giorno a solo {price}€ su Amazon ✨",
            f"Tutti mi chiedono dove l'ho presa: borsa viralissima a {price}€!"
        ]
        sd_prompt = (
            f"Commercial product display of {short_title}, placed on an elegant marble table, "
            f"soft warm studio spotlight, aesthetic minimalist boutique background, depth of field, 8k resolution, photorealistic"
        )
        bg_style = "Luxury Marble Studio"

    elif category == "clothing":
        hooks = [
            f"Questo capo da {price}€ risolve tutti i tuoi outfit della settimana 👗",
            f"Outfit da urlo su Amazon: questo vestito costa solo {price}€!",
            f"Non spendere centinaia di euro: questo capo a {price}€ è identico ai brand top ✨"
        ]
        sd_prompt = (
            f"Fashion editorial showcase of {short_title}, displayed on a sleek designer coat hanger, "
            f"warm aesthetic walk-in closet background, soft neutral ambient light, magazine aesthetic, highly detailed"
        )
        bg_style = "Walk-in Closet / Editorial"

    elif category == "shoes":
        hooks = [
            f"Le scarpe più comode ed eleganti della stagione a solo {price}€ 👟",
            f"Svolta look per i tuoi piedi: trovate su Amazon a {price}€!"
        ]
        sd_prompt = (
            f"Clean footwear advertisement of {short_title}, modern podium display, "
            f"dramatic side lighting, urban aesthetic background, 8k resolution"
        )
        bg_style = "Modern Footwear Podium"

    else:  # General Fashion / Accessories
        hooks = [
            f"L'accessorio definitivo che sta spopolando a solo {price}€ ✨",
            f"Troppo figo per costare solo {price}€ su Amazon! 🔥"
        ]
        sd_prompt = (
            f"High-end product photography of {short_title}, aesthetic wooden desk background, "
            f"natural window sunlight, warm cozy vibes, ultra detailed"
        )
        bg_style = "Cozy Aesthetic Desk"

    selected_hook = hooks[index % len(hooks)]
    sd_negative = "blurry, dark, ugly, distorted, low quality, noise, bad lighting"

    return selected_hook, sd_prompt, sd_negative, bg_style


def generate_tiktok_content(csv_input="amazon_fashion_trends.csv", output_file="tiktok_ready_posts.csv"):
    if not os.path.exists(csv_input):
        print(f"❌ Errore: Il file {csv_input} non esiste.")
        return

    df = pd.read_csv(csv_input)
    print(f"📖 Letti {len(df)} prodotti. Generazione Smart Content in corso...\n")

    posts_data = []

    for index, row in df.iterrows():
        title = str(row['title'])
        price = row['price']
        rating = row['rating']
        url = row['url']
        img_path = row.get('image_path', 'N/D')

        short_title = title.split(',')[0].strip()

        # Rilevamento automatico della categoria
        category = detect_category(title)

        # Generazione Prompt & Hook contestuali
        hook, sd_prompt, sd_negative, bg_style = get_smart_prompt_and_hook(category, short_title, price, index)

        caption = (
            f"{hook}\n\n"
            f"⭐ Valutazione: {rating}\n"
            f"💸 Prezzo: {price}€\n\n"
            f"🔗 Link diretto in bio al N. #{index + 1}! #amazonfinds #{category} #moda #outfitinspo"
        )

        posts_data.append({
            "ID": index + 1,
            "Categoria Rilevata": category,
            "Prodotto": short_title,
            "Prezzo": f"{price}€",
            "Immagine Originale": img_path,
            "TikTok Hook": hook,
            "Caption Completa": caption,
            "Stile Sfondo": bg_style,
            "Prompt AI Sfondo": sd_prompt,
            "Negative Prompt AI": sd_negative,
            "Link Affiliato": url
        })

    output_df = pd.DataFrame(posts_data)
    output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"🚀 {len(posts_data)} post categorizzati e salvati in '{output_file}'!\n")


if __name__ == "__main__":
    generate_tiktok_content()