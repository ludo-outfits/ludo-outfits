import os
import pandas as pd

STORE_ID = "hiberias-21"
INPUT_CSV = "tiktok_ready_posts.csv"
OUTPUT_CSV = "tiktok_ready_posts_with_links.csv"


def genera_link_affiliati():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ Errore: Il file '{INPUT_CSV}' non esiste. Esegui prima lo scraper!")
        return

    df = pd.read_csv(INPUT_CSV)

    # Costruzione automatica del link di affiliazione per ogni ASIN (colonna 'ID')
    df['Link Affiliato'] = df['ID'].apply(lambda asin: f"https://www.amazon.it/dp/{str(asin).strip()}?tag={STORE_ID}")

    # Salva il nuovo CSV arricchito con i link
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"✅ Generati {len(df)} link affiliati con StoreID '{STORE_ID}'!")
    print(f"📁 Salvato file aggiornato: '{OUTPUT_CSV}'\n")

    # Anteprima di verifica
    print("🔍 Esempio di link generati:")
    for _, row in df.head(3).iterrows():
        print(f"  • {row['Prodotto']} ({row['Fascia Prezzo']}): {row['Link Affiliato']}")


if __name__ == "__main__":
    genera_link_affiliati()