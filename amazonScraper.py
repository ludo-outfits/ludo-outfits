import os
import re
import hashlib
import time
import pandas as pd
import requests
from playwright.sync_api import sync_playwright

os.environ["ONNXRUNTIME_EXECUTION_PROVIDERS"] = "['CPUExecutionProvider']"

# Dizionario completo con 100 categorie e relative etichette pulite
category_mapping = {
    "borsa donna tracolla": "borse a tracolla",
    "vestito elegante donna": "abiti eleganti",
    "pantaloni palazzo donna": "pantaloni palazzo",
    "blazer donna casual": "blazer casual",
    "scarpe con tacco donna": "scarpe con tacco",
    "occhiali da sole donna": "occhiali da sole",
    "gioielli donna acciaio": "gioielli in acciaio",
    "scarpe sportive donna": "sneaker trendy",
    "borsa shopper donna": "borse shopper",
    "zaino casual donna": "zaini casual",
    "stivaletti donna invernali": "stivaletti eleganti",
    "gonna midi plissettata": "gonne plissettate",
    "cappotto lungo lana": "cappotti in lana",
    "giacca pelle ecologica donna": "giacche in eco-pelle",
    "mocassini donna eleganti": "mocassini chic",
    "ballerine donna pelle": "ballerine in pelle",
    "sandali gioiello donna": "sandali gioiello",
    "marsupio elegante donna": "marsupi chic",
    "pochette da sera donna": "pochette da sera",
    "portafoglio donna pelle": "portafogli chic",
    "cintura alta donna": "cinture da vita",
    "cappello lana inverno": "cappelli in maglia",
    "sciarpa cashmere donna": "sciarpe morbide",
    "foulard seta elegante": "foulard in seta",
    "orologio acciaio donna": "orologi eleganti",
    "set orecchini cerchio": "orecchini a cerchio",
    "collana girocollo oro": "collane punto luce",
    "anelli regolabili argento": "anelli luminosi",
    "bracciale tennis argento": "bracciali tennis",
    "felpa oversize donna": "felpe oversize",
    "maglione collo alto": "maglioni a collo alto",
    "cardigan lungo donna": "cardigan morbidi",
    "top corset elegante": "top corset",
    "body pizzo nero": "body in pizzo",
    "shorts jeans vita alta": "shorts di jeans",
    "leggings push up": "leggings push-up",
    "tuta jumpsuit elegante": "tute jumpsuit",
    "trench coat beige": "trench classici",
    "piumino corto lucido": "piumini corti",
    "gilet imbottito donna": "gilet trapuntati",
    "tailleur pantalone donna": "tailleur eleganti",
    "pigiama seta lungo": "pigiami in seta",
    "accappatoio spugna morbido": "kimono da casa",
    "pantofole pelo calde": "pantofole soffici",
    "bikini brasiliana mare": "bikini alla moda",
    "costume intero scollato": "costumi interi",
    "copricostume pizzo mare": "copricostumi chic",
    "kimono lungo estivo": "kimono stampati",
    "caftano spiaggia elegante": "caftani leggeri",
    "vestito lungo floreale": "abiti floreali",
    "minidress paillettes": "abiti con paillettes",
    "gonna jeans lunga": "gonne di jeans lunghe",
    "pantaloni cargo tasconi": "pantaloni cargo",
    "jeans flared zampa": "jeans a zampa",
    "jeans boyfriend strappi": "jeans boyfriend",
    "leggings termici invernali": "leggings effetto pelle",
    "sottoveste elegante seta": "abiti sottoveste",
    "corsetto modellante donna": "corsetti stringati",
    "calzini particolari pizzo": "calzini con fiocco",
    "collant velati fantasia": "collant velati chic",
    "cerchietto capelli imbottito": "cerchietti in velluto",
    "fermagli per capelli perle": "mollette gioiello",
    "elastici capelli seta scrunchie": "scrunchie in raso",
    "zainetto piccolo ecopelle": "zainetti chic",
    "borsa secchiello pelle": "borse a secchiello",
    "borsa trapezio elegante": "borse rigide",
    "stivali alti cuoio": "stivali sopra il ginocchio",
    "anfibi platform donna": "anfibi platform",
    "espadrillas zeppa corda": "espadrillas con zeppa",
    "sabot tacco comodo": "sabot con tacco",
    "mules aperte tacco": "mules eleganti",
    "infradito gioiello mare": "infradito gioiello",
    "cappello paglia tesa larga": "cappelli in paglia",
    "occhiali da vista montatura cat eye": "occhiali da sole cat-eye",
    "porta carte credito pelle": "mini borse da spalla",
    "guanti pelle touchscreen": "guanti eleganti",
    "ombrello compatto antivento": "top monospalla",
    "scaldacollo lana morbida": "scialli eleganti",
    "berretto lana pon pon": "baschi alla francese",
    "felpa con cappuccio zip": "crop top sportivi",
    "tuta sportiva chic": "tute da riposo chic",
    "pantaloncini ciclista sportivi": "biker shorts",
    "top sportivo spalline": "top incrociati",
    "reggiseno balconcino pizzo": "bralette in pizzo",
    "slip brasiliana pizzo": "intimo in pizzo",
    "mutandine modellanti seamless": "body contenitivi",
    "vestito 3/4 midi ufficio": "abiti midi eleganti",
    "blazer oversize monopetto": "blazer oversize",
    "giacca denim cropped": "giacche di jeans cropped",
    "gonna satin midi": "gonne midi in raso",
    "pantaloni culotte eleganti": "pantaloni culotte",
    "pantaloni jogger satin": "pantaloni in raso",
    "camicia oversize bianca": "camicie bianche oversize",
    "blusa elegante maniche a sbuffo": "bluse con maniche a sbuffo",
    "maglia collo polo donna": "maglioni traforati",
    "gilet maglia trecce": "gilet in maglia",
    "cappotto teddy bear": "cappotti teddy",
    "giacca biker pelle": "giacche biker",
    "stivaletti chelsea pelle": "stivaletti bassi chic",
    "scarpe slingback tacco basso": "scarpe slingback",
    "borsa bauletto vintage": "borse a bauletto",
    "collana catena grossa": "collane a catena",
    "bracciale rigido acciaio": "bracciali rigidi"
}


def smart_clean_title(full_title):
    clean = str(full_title).strip()
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = re.sub(r'\[.*?\]', '', clean)
    for delimiter in ['-', '–', '|', ',']:
        if delimiter in clean:
            part = clean.split(delimiter)[0].strip()
            if len(part) > 2:
                clean = part
                break
    stop_words = {
        'da', 'di', 'con', 'per', 'in', 'un', 'una', 'e', 'del', 'della',
        'il', 'la', 'lo', 'gli', 'le', 'i', 'uno', 'donna', 'uomo', 'pezzi', 'pcs', 'set',
        'elegante', 'casual', 'corto', 'lungo', 'estivo', 'invernale', 'sexy', 'sportivo',
        'comodo', 'nuovo', 'fantasia', 'tinta', 'unita', 'oversize', 'ampio'
    }
    words = [w for w in clean.split() if w.lower() not in stop_words]
    if words:
        clean = " ".join(words[:2])
    else:
        clean = str(full_title).split()[0]
    if len(clean) > 20:
        words_fallback = clean.split()
        clean = words_fallback[0] if words_fallback else "FASHION"
    if len(clean) < 2:
        clean = "FASHION ITEM"
    return clean.upper()


def parse_rating_value(rating_str):
    try:
        match = re.search(r'(\d+[\.,]\d+)', rating_str)
        if match:
            return float(match.group(1).replace(',', '.'))
    except Exception:
        pass
    return 4.3


def parse_reviews_count(item):
    """Estrae il numero di recensioni per determinare la popolarità del prodotto"""
    try:
        review_el = item.locator("span.a-size-base.s-underline-text").first
        if review_el.count() > 0:
            text = review_el.inner_text().replace(".", "").replace(",", "").strip()
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
    except Exception:
        pass
    return 50  # Valore di default medio se non trovato


def generate_procedural_review(asin):
    """Genera una recensione breve, efficace e rigorosamente gender-neutral."""
    hash_val = int(hashlib.md5(asin.encode()).hexdigest(), 16)

    universal_reviews = [
        "Super comodo!", "Rapporto qualità-prezzo top.", "Leggero e pratico.",
        "Dal vivo è ancora più bello.", "Spettacolare davvero.", "Qualità sorprendente.",
        "Top assoluto!", "Troppo bello.", "Un vero affare.", "Curato nei minimi dettagli.",
        "Da usare continuamente.", "Eleganza pura.", "Ricevuto un sacco di complimenti.",
        "Scelta impeccabile.", "Dettagli pazzeschi.", "Semplice ma d'effetto.",
        "Stile unico.", "Pezzo imperdibile.", "Bello da impazzire.", "Raffinato e stiloso.",
        "Acquisto azzeccatissimo.", "Top del top.", "Favoloso.", "Rifinito alla perfezione.",
        "Look super chic.", "Super approvato!", "Design pazzesco.", "Qualità eccellente.",
        "Un must have assoluto.", "Soddisfazione totale!", "Impossibile farne a meno.",
        "Di altissimo livello.", "Molto versatile.", "Colore pazzesco dal vivo.",
        "Fatto benissimo.", "Super consigliato!", "Dà un tocco chic immediato.",
        "Pezzo perfetto.", "Stupenda sorpresa.", "Resa eccezionale!",
        "Bellissimo da vedere e indossare.", "Un vero gioiellino.", "Stile da vendere.",
        "Super versatile.", "Elegante e di classe.", "Qualità superiore!",
        "Ottima vestibilità.", "Veramente di qualità.", "Fa una gran figura.",
        "Confezione e resa top.", "Super piacevole.", "Rende qualsiasi outfit unico.",
        "Un dettaglio che fa la differenza.", "Qualità oltre le aspettative.", "Perfetta visuale.",
        "Resa estetica pazzesca.", "Si nota subito la cura.", "Estremamente piacevole.",
        "Top per ogni occasione.", "Impeccabile in tutto.", "Vestibilità ideale.",
        "Un mai più senza.", "Stile pulito ed elegante.", "Davvero super chic.",
        "Soddisfa ogni aspettativa.", "Design moderno e pulito.", "Fa la sua figura.",
        "Super versatile e pratico.", "Un'ottima scelta.", "Materiali di livello.",
        "Super curato nei dettagli.", "Sempre una garanzia.", "Raffinatezza unica.",
        "Look garantito.", "Punto di forza dell'outfit.", "Ottima fattura.",
        "Veramente ben fatto.", "Davvero un ottimo pezzo.", "Sempre al top.",
        "Super pratico e di stile.", "Colpisce subito.", "Dettagli davvero curati.",
        "Qualità eccezionale.", "Svolta qualsiasi combinazione.", "Pezzo di tendenza.",
        "Look subito curato.", "Davvero irrinunciabile.", "Risultato pazzesco!",
        "Elegante senza sforzo.", "Resa dal vivo incredibile.", "Molto fine e curato.",
        "Impatto visivo super.", "Assolutamente da avere.", "Stile minimale e chic.",
        "Top per la stagione.", "Un dettaglio di gran classe.", "Davvero piacevole.",
        "Incredibile rapporto qualità prezzo.", "Promosso a pieni voti!"
    ]
    return universal_reviews[hash_val % len(universal_reviews)]


def fetch_items_from_page(page, min_rating=3.8):
    items = page.locator("div.s-result-item[data-asin]").all()
    page_data = []

    img_dir = "temp_images"
    os.makedirs(img_dir, exist_ok=True)

    for item in items:
        asin = item.get_attribute("data-asin")
        if not asin or len(asin.strip()) == 0:
            continue
        try:
            rating_el = item.locator("span.a-icon-alt").first
            rating = rating_el.inner_text() if rating_el.count() > 0 else "4,3 su 5 stelle"
            numeric_rating = parse_rating_value(rating)

            if numeric_rating < min_rating:
                continue

            reviews_count = parse_reviews_count(item)

            title = ""
            for selector in ["h2 a span", "span.a-text-normal", "h2 span"]:
                el = item.locator(selector).first
                if el.count() > 0:
                    txt = el.inner_text().strip()
                    if txt and len(txt) > 3:
                        title = txt
                        break
            if not title:
                continue
            clean_title = smart_clean_title(title)

            price = "0,00"
            numeric_price = 0.0
            price_whole = item.locator("span.a-price-whole").first
            price_fraction = item.locator("span.a-price-fraction").first
            if price_whole.count() > 0:
                w = price_whole.inner_text().replace(".", "").replace(",", "").strip()
                f = price_fraction.inner_text().strip() if price_fraction.count() > 0 else "00"
                price = f"{w},{f}"
                try:
                    numeric_price = float(f"{w}.{f}")
                except:
                    numeric_price = 0.0

            # Filtro anti-prezzi irrisori (sotto i 12€)
            if numeric_price < 12.0:
                continue

            img_el = item.locator("img.s-image").first
            img_url = img_el.get_attribute("src") if img_el.count() > 0 else ""
            img_path = ""
            if img_url:
                img_data = requests.get(img_url).content
                img_path = os.path.join(img_dir, f"temp_img_{asin}.jpg")
                with open(img_path, "wb") as handler:
                    handler.write(img_data)

            short_review = generate_procedural_review(asin)
            page_data.append({
                "ID": asin,
                "Titolo Originale": title,
                "Prodotto": clean_title,
                "Prezzo_Num": numeric_price,
                "Prezzo": price,
                "rating": rating,
                "Reviews_Count": reviews_count,
                "Recensione Top": short_review,
                "Immagine Originale": img_path
            })
        except Exception:
            continue
    return page_data


def scrape_amazon_fashion_category(search_query, items_per_tier=5, output_file="amazon_fashion_master.csv"):
    print(f"\n🔍 Avvio scraping su Amazon per: '{search_query}'...")
    raw_items_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="it-IT"
        )
        page = context.new_page()
        try:
            page.goto("https://www.amazon.it", timeout=60000)
            time.sleep(2)
            page.fill("input#twotabsearchtextbox", search_query)
            page.press("input#twotabsearchtextbox", "Enter")
            page.wait_for_selector("div.s-main-slot", timeout=15000)
            time.sleep(2)
            raw_items_data.extend(fetch_items_from_page(page, min_rating=3.8))

            next_button = page.locator("a.s-pagination-next").first
            if next_button.count() > 0 and len(raw_items_data) < 30:
                try:
                    next_button.click()
                    page.wait_for_selector("div.s-main-slot", timeout=15000)
                    time.sleep(2)
                    raw_items_data.extend(fetch_items_from_page(page, min_rating=3.8))
                except Exception:
                    pass
        except Exception as e:
            print(f"❌ Errore critico su '{search_query}': {e}")
        finally:
            browser.close()

    if raw_items_data:
        seen_titles = set()
        unique_items = []
        for item in raw_items_data:
            if item["Prodotto"] not in seen_titles:
                seen_titles.add(item["Prodotto"])
                unique_items.append(item)

        unique_items.sort(key=lambda x: (x["Reviews_Count"], x["Prezzo_Num"]), reverse=True)
        unique_items.sort(key=lambda x: x["Prezzo_Num"])

        if len(unique_items) >= (items_per_tier * 2):
            mid_point = len(unique_items) // 2
            low_cost_pool = unique_items[:mid_point]
            media_pool = unique_items[mid_point:]

            low_cost_pool.sort(key=lambda x: x["Reviews_Count"], reverse=True)
            media_pool.sort(key=lambda x: x["Reviews_Count"], reverse=True)

            low_cost_final = low_cost_pool[:items_per_tier]
            media_final = media_pool[:items_per_tier]
        else:
            low_cost_final = unique_items[:items_per_tier]
            media_final = unique_items[items_per_tier:items_per_tier * 2]

        final_products = []
        display_label = category_mapping.get(search_query, search_query)

        for p in low_cost_final:
            p["Categoria"] = search_query
            p["Etichetta Pulita"] = display_label
            p["Fascia Prezzo"] = "Low Cost"
            del p["Prezzo_Num"]
            del p["Reviews_Count"]
            final_products.append(p)

        for p in media_final:
            p["Categoria"] = search_query
            p["Etichetta Pulita"] = display_label
            p["Fascia Prezzo"] = "Media Categoria"
            del p["Prezzo_Num"]
            del p["Reviews_Count"]
            final_products.append(p)

        df_new = pd.DataFrame(final_products)
        if os.path.exists(output_file):
            df_old = pd.read_csv(output_file)
            df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=["ID", "Fascia Prezzo"])
        else:
            df_combined = df_new

        df_combined.to_csv(output_file, index=False, encoding="utf-8-sig")
        df_combined.to_csv("tiktok_ready_posts.csv", index=False, encoding="utf-8-sig")
        print(f"\n🚀 Categoria '{search_query}' completata con 5 Low Cost e 5 Media Categoria popolari!")


def run_mass_scraping():
    for query in category_mapping.keys():
        scrape_amazon_fashion_category(search_query=query, items_per_tier=5)
        print("⏳ Pausa di sicurezza tra le categorie...")
        time.sleep(3)


if __name__ == "__main__":
    run_mass_scraping()