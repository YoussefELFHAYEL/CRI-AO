"""
CRI-RSK Chatbot — Query transformation service.
Rewrites user queries to improve retrieval quality.
Uses Google Gemini for query rewriting.
"""

import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

QUERY_REWRITE_PROMPT = """Tu es un assistant spécialisé dans l'investissement au Maroc et le CRI (Centre Régional d'Investissement) de Rabat-Salé-Kénitra.

Reformule la question de l'utilisateur pour améliorer la recherche dans une base de connaissances vectorielle. Tu dois respecter scrupuleusement ces règles :
1. Corriger les fautes d'orthographe et la grammaire.
2. Développer les abréviations connues (SARL, SA, SNC, AMDI, etc.).
3. Rendre la question plus précise TOUT EN CONSERVANT INTACTS les noms propres, les secteurs (ex: Pêche maritime, GIAC, Tertiaire, etc) et le métier inscrits par l'utilisateur ! Ne généralise jamais la question en supprimant les mots clés importants.
4. Garder la même langue que la question originale.
5. Si la question est en darija/dialecte marocain, reformule en arabe classique ou en français.

Exemples :
- "créer boite" → "Quelles sont les étapes pour créer une entreprise au Maroc ?"
- "docs SARL" → "Quels sont les documents requis pour la création d'une Société à Responsabilité Limitée (SARL) ?"
- "بغيت نفتح شركة" → "ما هي إجراءات تأسيس شركة في المغرب؟"
- "incitations pour GIAC Pêche maritime" → "Quelles sont les incitations et subventions disponibles pour les entreprises du secteur GIAC Pêche maritime ?"

Réponds UNIQUEMENT avec la question reformulée, sans aucune explication."""


async def transform_query(
    query: str,
    llm_model: str = "gemini-2.5-flash",
    api_key: str = "",
) -> str:
    """
    Transform a user query to improve retrieval.
    Returns the rewritten query.
    Falls back to the original query on error.
    """
    # Skip transformation for very short or very clear queries
    if len(query.strip()) < 5:
        return query

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=llm_model,
            contents=f"Question originale: {query}",
            config=types.GenerateContentConfig(
                system_instruction=QUERY_REWRITE_PROMPT,
                temperature=0,
                max_output_tokens=1000,
            ),
        )

        rewritten = response.text.strip() if response.text else ""

        # Validation: If rewritten query is significantly shorter than original, 
        # it might be truncated or failed.
        if len(rewritten) < len(query) * 0.5:
            logger.warning(f"Transformed query seems truncated ('{rewritten}'), using original")
            return query

        if rewritten:
            logger.info(
                f"Query transformed: '{query[:50]}' → '{rewritten[:50]}'"
            )
            return rewritten
        return query

    except Exception as e:
        logger.warning(f"Query transformation failed: {e}")
        return query
