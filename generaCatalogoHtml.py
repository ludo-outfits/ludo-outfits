import os
import pandas as pd


def genera_catalogo_html(csv_input="tiktok_ready_posts_with_links.csv", output_html="index.html"):
    if not os.path.exists(csv_input):
        print(f"❌ Errore: Il file '{csv_input}' non esiste.")
        return

    df = pd.read_csv(csv_input)
    print("🌐 Generazione del catalogo con Menu Categorie per Mobile...")

    categorie = sorted(df["Etichetta Pulita"].unique())

    html_content = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Ludo Outfits | Amazon Shop</title>
    <style>
        :root {
            --bg-color: #EFEBD3;
            --card-bg: #FFFFFF;
            --primary-bordeaux: #4E1C26;
            --text-main: #34281F;
            --text-sub: #5F4E41;
        }

        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        header {
            width: 100%;
            max-width: 480px;
            padding: 25px 15px 10px 15px;
            text-align: center;
        }

        .profile-img {
            width: 75px;
            height: 75px;
            border-radius: 50%;
            background-color: var(--primary-bordeaux);
            color: #FFF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            margin: 0 auto 10px auto;
            box-shadow: 0 4px 10px rgba(78, 28, 38, 0.2);
        }

        h1 {
            font-size: 20px;
            color: var(--primary-bordeaux);
            margin: 0 0 4px 0;
        }

        p.subtitle {
            font-size: 13px;
            color: var(--text-sub);
            margin: 0 0 10px 0;
        }

        /* 🧭 BARRA CATEGORIE CON MENU A TENDINA (DROPDOWN MOBILE) */
        .nav-categories-bar {
            width: 100%;
            max-width: 480px;
            background: rgba(239, 235, 211, 0.98);
            position: sticky;
            top: 0;
            z-index: 1000;
            padding: 10px 15px;
            border-bottom: 1px solid rgba(78, 28, 38, 0.12);
            backdrop-filter: blur(8px);
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .category-select {
            flex-grow: 1;
            background-color: #FFFFFF;
            color: var(--primary-bordeaux);
            border: 2px solid var(--primary-bordeaux);
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 700;
            outline: none;
            cursor: pointer;
            appearance: none;
            -webkit-appearance: none;
            background-image: url("data:image/svg+xml;utf8,<svg fill='%234E1C26' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/></svg>");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 18px;
        }

        .btn-reset {
            background-color: var(--primary-bordeaux);
            color: white;
            border: none;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }

        .container {
            width: 100%;
            max-width: 480px;
            padding: 15px;
        }

        .category-section {
            margin-bottom: 30px;
        }

        .category-title {
            font-size: 15px;
            font-weight: 700;
            color: var(--primary-bordeaux);
            border-bottom: 2px solid var(--primary-bordeaux);
            padding-bottom: 4px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .product-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .product-card {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 2px 8px rgba(52, 40, 31, 0.05);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .product-img-container {
            width: 100%;
            height: 130px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #FAFAFA;
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 8px;
        }

        .product-img-container img {
            max-height: 100%;
            max-width: 100%;
            object-fit: contain;
        }

        .product-title {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-main);
            margin: 0 0 6px 0;
            line-height: 1.25;
            height: 28px;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }

        .product-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .price {
            font-size: 13px;
            font-weight: 700;
            color: var(--primary-bordeaux);
        }

        .tier-badge {
            font-size: 9px;
            padding: 2px 5px;
            border-radius: 4px;
            background: #F0E6D8;
            color: var(--text-sub);
            font-weight: 600;
        }

        .btn-buy {
            display: block;
            width: 100%;
            background-color: var(--primary-bordeaux);
            color: white;
            text-align: center;
            padding: 7px 0;
            border-radius: 6px;
            text-decoration: none;
            font-size: 11px;
            font-weight: 600;
        }

        footer {
            text-align: center;
            padding: 20px 15px;
            font-size: 11px;
            color: var(--text-sub);
            margin-top: auto;
        }
    </style>
</head>
<body>

    <header>
        <div class="profile-img">LO</div>
        <h1>@ludo_outfits</h1>
        <p class="subtitle">I miei look e accessori preferiti su Amazon ✨</p>
    </header>

    <!-- 🧭 Menu Categorie a Tendina -->
    <div class="nav-categories-bar">
        <select class="category-select" id="catSelector" onchange="onCategorySelect(this.value)">
            <option value="all">🔍 Scegli Categoria (Tutte)...</option>
"""

    for cat in categorie:
        cat_id = cat.replace(" ", "_").replace("'", "")
        html_content += f'            <option value="{cat_id}">{cat.capitalize()}</option>\n'

    html_content += """        </select>
        <button class="btn-reset" onclick="resetCategories()">Tutti</button>
    </div>

    <div class="container">
"""

    grouped = df.groupby("Etichetta Pulita")

    for categoria, group in grouped:
        cat_id = categoria.replace(" ", "_").replace("'", "")
        html_content += f"""
        <div class="category-section" id="{cat_id}">
            <div class="category-title">{categoria}</div>
            <div class="product-grid">
"""
        for _, row in group.iterrows():
            titolo = row.get("Prodotto", "Item")
            prezzo = row.get("Prezzo", "0,00")
            link = row.get("Link Affiliato", "#")
            fascia = row.get("Fascia Prezzo", "")
            img_path = row.get("Immagine Originale", "")

            html_content += f"""
                <div class="product-card">
                    <div>
                        <div class="product-img-container">
                            <img src="{img_path}" alt="{titolo}" loading="lazy">
                        </div>
                        <div class="product-info">
                            <h2 class="product-title">{titolo}</h2>
                            <div class="product-meta">
                                <span class="price">{prezzo}€</span>
                                <span class="tier-badge">{fascia}</span>
                            </div>
                        </div>
                    </div>
                    <a href="{link}" target="_blank" class="btn-buy">Vedi su Amazon 🛍️</a>
                </div>
"""
        html_content += """
            </div>
        </div>
"""

    html_content += """
    </div>

    <footer>
        <p>© 2026 Ludo Outfits • In qualità di Affiliato Amazon ricevo un guadagno dagli acquisti idonei.</p>
    </footer>

    <script>
        function onCategorySelect(catId) {
            const sections = document.querySelectorAll('.category-section');
            sections.forEach(sec => {
                if (catId === 'all' || sec.id === catId) {
                    sec.style.display = 'block';
                } else {
                    sec.style.display = 'none';
                }
            });
            window.scrollTo({ top: 100, behavior: 'smooth' });
        }

        function resetCategories() {
            document.getElementById('catSelector').value = 'all';
            onCategorySelect('all');
        }
    </script>

</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✨ Catalogo Mobile con Menu Dropdown generato -> '{output_html}'!")


if __name__ == "__main__":
    genera_catalogo_html()