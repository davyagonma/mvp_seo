import os
import json
import streamlit as st
import google.generativeai as genai

# Configure API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Prompt template
BRIEF_PROMPT = """Tu es un expert SEO senior. Tâche: produire un brief complet.
Contrainte: langue {lang}. Ton: {tone}. Marque: {brand}.
Mot-clé racine: "{keyword}"

Donne un JSON STRICT:
{{
  "search_intent": "...",
  "outline": [ "H2: ...", "H3: ...", "..."],
  "faqs": [ "...", "..."],
  "titles": [ "Titre 1", "Titre 2", "..."],
  "meta_description": "...",
  "internal_links_suggestions": [ "slug-1", "slug-2" ]
}}
Répond uniquement en JSON.
"""



def generate_brief(keyword: str, lang: str, tone: str, brand: str | None) -> dict:
    prompt = BRIEF_PROMPT.format(keyword=keyword, lang=lang, tone=tone, brand=brand or "")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    # Gemini renvoie souvent du texte brut, parfois avec ```json
    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("` \n").replace("json", "", 1).strip()
    return json.loads(text)


# --- UI ---
st.set_page_config(page_title="SEO Brief Generator", page_icon="📈", layout="wide")
st.title("📈 SEO Brief Generator")
st.markdown("Générez des briefs SEO complets à partir d'un mot-clé en quelques secondes.")

with st.form("brief_form"):
    keyword = st.text_input("Mot-clé", placeholder="ex: création site vitrine")
    lang = st.selectbox("Langue", ["fr", "en", "es", "de"], index=0)
    tone = st.selectbox("Ton", ["informatif", "persuasif", "créatif"])
    brand = st.text_input("Marque (optionnel)")
    submitted = st.form_submit_button("🚀 Générer le brief")

if submitted and keyword:
    with st.spinner("Génération en cours..."):
        try:
            brief = generate_brief(keyword, lang, tone, brand)
            st.subheader("🎯 Search Intent")
            st.write(brief.get("search_intent", ""))

            st.subheader("📋 Outline")
            st.markdown("\n".join([f"- {o}" for o in brief.get("outline", [])]))

            st.subheader("❓ FAQs")
            st.markdown("\n".join([f"- {q}" for q in brief.get("faqs", [])]))

            st.subheader("📝 Titles")
            st.markdown("\n".join([f"- {t}" for t in brief.get("titles", [])]))

            st.subheader("🔍 Meta Description")
            st.write(brief.get("meta_description", ""))

            st.subheader("🔗 Liens internes suggérés")
            st.markdown("\n".join([f"- {l}" for l in brief.get("internal_links_suggestions", [])]))
        except Exception as e:
            st.error(f"Erreur: {e}")
