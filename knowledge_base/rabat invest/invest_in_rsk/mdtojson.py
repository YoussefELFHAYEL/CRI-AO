"""
md_to_json_extractor.py
Extracts structured incentive JSONs from scraped markdown data.
"""

import re
import json
import os
import hashlib
from typing import Dict, List, Optional


# ============================================================
# SECTOR & SIZE MAPPING CONFIGURATION
# ============================================================

SECTOR_MAPPING = {
    # Maps keywords found in "cible" and "secteurs" fields
    # to the 6 chatbot buttons
    "industrie": [
        "industri", "manufactur", "usine", "product",
        "mécani", "métallur", "électr", "électron",
        "chimi", "parachimi", "plastur", "caoutchouc",
        "bois", "ameublement", "agroaliment", "agro-industr",
        "textile", "cuir", "habillement", "artisan",
        "minier", "hydrocarbur", "pharma", "aéronaut",
        "automobi", "offshoring", "externalisation"
    ],
    "services": [
        "service", "hôtel", "touris", "hébergement",
        "restaur", "transport", "logisti", "banqu",
        "offshore", "holding", "financ", "assurance",
        "enseignement", "formation", "éducation", "sport",
        "santé", "conseil", "expertise"
    ],
    "agriculture": [
        "agricol", "agricult", "élevage", "éleveur",
        "irrigation", "foncier", "semence", "plantation",
        "génétique", "bovin", "ovin", "caprin",
        "camelin", "apicul", "abeille", "pêche",
        "aquacul", "rural", "agrég", "lait",
        "olive", "agrume", "céréal", "sucr"
    ],
    "tech": [
        "tech", "numér", "digital", "informati",
        "TIC", "start-up", "startup", "innov",
        "logiciel", "développement", "IT", "ITO",
        "BPO", "KPO", "ESO", "cloud",
        "e-commerce", "cyber", "data", "IA"
    ],
    "btp": [
        "BTP", "construct", "bâtiment", "travaux publics",
        "immobili", "promoteur", "logement", "habitat",
        "ciment", "béton", "géotechni", "chantier"
    ],
    "commerce": [
        "commerc", "distribu", "export", "import",
        "négoce", "vente", "marché", "grossist",
        "détail"
    ]
}

SIZE_MAPPING = {
    "tpe": [
        "TPE", "très petite", "auto-entrepreneur",
        "auto entrepreneur", "micro", "porteur de projet",
        "personne physique", "individuel"
    ],
    "pme": [
        "PME", "petite ou moyenne", "petite et moyenne",
        "TPME", "moyenne entreprise"
    ],
    "ge": [
        "GE", "grande entreprise", "toutes tailles",
        "sociétés"
    ]
}

LOCATION_KEYWORDS = {
    "rabat": ["rabat"],
    "sale": ["salé", "sale"],
    "kenitra": ["kénitra", "kenitra"],
    "sidi_slimane": ["sidi slimane"],
    "khemisset": ["khemisset"],
    "sidi_kacem": ["sidi kacem"],
    "toute_region": [
        "national", "maroc", "tout le territoire",
        "toutes les régions"
    ]
}


# ============================================================
# MARKDOWN PARSER
# ============================================================

class IncentiveExtractor:
    """Parses the scraped MD and produces structured JSONs."""

    def __init__(self, md_content: str):
        self.md_content = md_content
        self.raw_blocks = []
        self.json_documents = []
        self.counter = 0
        self.collection_counters = {}

    def parse(self) -> List[Dict]:
        """Main entry point: parse MD → list of dicts."""
        self._split_into_blocks()
        self._process_blocks()
        return self.json_documents

    def _split_into_blocks(self):
        """
        Split the MD into individual incentive blocks.

        Each block is delimited by the pattern:
          axe\n<axe_value>\nincitation\n<incitation_value>\n
          consistance\n<consistance_value>\n...
        """
        # Split on the "axe" field delimiter pattern
        # The scraped data uses consistent field headers
        pattern = r'(?=\naxe\n)'
        parts = re.split(pattern, self.md_content)

        for part in parts:
            part = part.strip()
            if not part or len(part) < 50:
                continue
            self.raw_blocks.append(part)

        print(f"Found {len(self.raw_blocks)} raw blocks")

    def _extract_field(self, block: str, field: str) -> str:
        """Extract a field value from a block."""
        # Pattern: field name on its own line,
        # followed by content until next field
        fields = [
            "axe", "incitation", "consistance",
            "organisation", "Cible", "cible",
            "Critères d'éligibilité Conditions",
            "Modalités de mise en œuvre",
            "Liste de pièces à fournir",
            "Coordonnées"
        ]

        # Normalize field name for search
        field_lower = field.lower()
        field_pattern = re.escape(field)

        # Find the field and extract until next field
        next_fields = [f for f in fields
                       if f.lower() != field_lower]
        next_pattern = "|".join(
            [re.escape(f) for f in next_fields]
        )

        pattern = (
            rf'\n{field_pattern}\s*\n'
            rf'(.*?)'
            rf'(?:\n(?:{next_pattern})\s*\n|\Z)'
        )
        match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)

        if match:
            return match.group(1).strip()
        return ""

    def _determine_collection(self, axe: str, org: str) -> str:
        """Determine collection letter based on content."""
        axe_lower = axe.lower()
        org_lower = org.lower()

        if "conventionnel" in axe_lower or "charte" in axe_lower:
            return "A"
        if "maroc pme" in org_lower:
            return "B"
        if "tamwilcom" in org_lower or "ccg" in org_lower:
            return "C"
        if "finea" in org_lower:
            return "D"
        if "numeric fund" in org_lower or "cgem" in org_lower:
            return "E"
        if "agricol" in axe_lower and "fiscal" not in axe_lower:
            return "F"
        if "export" in axe_lower or "indh" in axe_lower:
            return "G"
        if "fiscal" in axe_lower:
            return "H"
        if "mre" in axe_lower or "résidant" in axe_lower:
            return "I"
        if ("formation" in axe_lower or "emploi" in axe_lower
                or "giac" in org_lower or "anapec" in org_lower
                or "ofppt" in org_lower or "cetie" in org_lower
                or "cerimme" in org_lower or "cetemco" in org_lower
                or "ctpc" in org_lower or "ctth" in org_lower
                or "ctiba" in org_lower or "cetia" in org_lower
                or "cmtc" in org_lower):
            return "J"
        return "H"  # Default to fiscal

    def _determine_type(self, consistance: str, nom: str) -> str:
        """Determine incentive type."""
        text = (consistance + " " + nom).lower()

        if any(w in text for w in [
            "exonér", "exoneration", "taux réduit",
            "0%", "exemption"
        ]):
            return "exoneration"
        if any(w in text for w in [
            "subvention", "don", "prime d'investissement"
        ]):
            return "subvention"
        if any(w in text for w in [
            "prime", "contribution non remboursable"
        ]):
            return "prime"
        if any(w in text for w in [
            "garantie", "damane", "quotité de garantie"
        ]):
            return "garantie"
        if any(w in text for w in [
            "financement", "crédit", "prêt", "avance",
            "cofinancement", "ligne"
        ]):
            return "financement"
        if any(w in text for w in [
            "accompagnement", "conseil", "expertise",
            "assistance", "formation", "coaching"
        ]):
            return "accompagnement"
        if any(w in text for w in ["formation", "giac", "csf"]):
            return "formation"

        return "autre"

    def _map_sectors(self, full_text: str) -> List[str]:
        """Map to chatbot sector buttons."""
        text_lower = full_text.lower()
        matched = []

        for sector, keywords in SECTOR_MAPPING.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    matched.append(sector)
                    break

        # If "tous les secteurs" or very broad
        if ("tous les secteurs" in text_lower
                or "tous secteurs" in text_lower
                or not matched):
            return [
                "industrie", "services", "agriculture",
                "tech", "btp", "commerce"
            ]

        return list(set(matched))

    def _map_sizes(self, cible_text: str) -> List[str]:
        """Map to chatbot size buttons."""
        text_lower = cible_text.lower()
        matched = []

        for size, keywords in SIZE_MAPPING.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    matched.append(size)
                    break

        if "toutes tailles" in text_lower or not matched:
            return ["tpe", "pme", "ge"]

        return list(set(matched))

    def _map_locations(self, full_text: str) -> List[str]:
        """Determine applicable locations."""
        text_lower = full_text.lower()

        # Check for territorial specifics
        if any(kw in text_lower for kw in [
            "sidi slimane", "khemisset", "sidi kacem"
        ]):
            locations = ["toute_region"]
            for loc, kws in LOCATION_KEYWORDS.items():
                for kw in kws:
                    if kw.lower() in text_lower:
                        locations.append(loc)
            return list(set(locations))

        # Default: available everywhere in the region
        return [
            "rabat", "sale", "kenitra", "toute_region"
        ]

    def _extract_numeric_condition(
        self, text: str, patterns: List[str]
    ) -> Optional[int]:
        """Extract numeric conditions from text."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                num_str = match.group(1).replace(
                    " ", ""
                ).replace(".", "")
                try:
                    return int(num_str)
                except ValueError:
                    continue
        return None

    def _generate_short_description(
        self, nom: str, consistance: str
    ) -> str:
        """Generate a concise description (1-2 sentences)."""
        # Take first 2 meaningful sentences
        sentences = re.split(r'[.!]\s', consistance)
        meaningful = [
            s.strip() for s in sentences
            if len(s.strip()) > 20
        ]
        if meaningful:
            desc = ". ".join(meaningful[:2])
            if len(desc) > 300:
                desc = desc[:297] + "..."
            return desc
        return nom

    def _generate_tags(
        self, nom: str, consistance: str, axe: str
    ) -> List[str]:
        """Generate search tags."""
        tags = []
        text = (nom + " " + consistance + " " + axe).lower()

        tag_keywords = [
            "exonération", "subvention", "prime", "garantie",
            "crédit", "financement", "formation", "emploi",
            "export", "investissement", "startup", "innovation",
            "digital", "vert", "durable", "femme", "jeune",
            "rural", "MRE", "TVA", "IS", "IR", "douane",
            "foncier", "immobilier", "agriculture", "industrie",
            "tourisme", "hôtel", "transport", "offshore",
            "artisanat", "pêche", "énergie", "environnement"
        ]

        for tag in tag_keywords:
            if tag.lower() in text:
                tags.append(tag)

        return tags

    def _extract_pieces(self, pieces_text: str) -> List[str]:
        """Extract list of required documents."""
        if not pieces_text:
            return []

        lines = pieces_text.strip().split("\n")
        pieces = []
        for line in lines:
            cleaned = re.sub(
                r'^[\d\.\-\•\*]+\s*', '', line.strip()
            )
            if cleaned and len(cleaned) > 5:
                pieces.append(cleaned)
        return pieces

    def _process_blocks(self):
        """Process all raw blocks into structured JSONs."""
        for block in self.raw_blocks:
            try:
                doc = self._process_single_block(block)
                if doc:
                    self.json_documents.append(doc)
            except Exception as e:
                print(f"Error processing block: {e}")
                continue

        print(
            f"Successfully extracted "
            f"{len(self.json_documents)} JSON documents"
        )

    def _process_single_block(
        self, block: str
    ) -> Optional[Dict]:
        """Process a single MD block into a JSON dict."""
        # Extract raw fields
        axe = self._extract_field(block, "axe")
        incitation = self._extract_field(block, "incitation")
        consistance = self._extract_field(
            block, "consistance"
        )
        organisation = self._extract_field(
            block, "organisation"
        )
        cible = self._extract_field(block, "Cible")
        if not cible:
            cible = self._extract_field(block, "cible")
        criteres = self._extract_field(
            block, "Critères d'éligibilité Conditions"
        )
        modalites = self._extract_field(
            block, "Modalités de mise en œuvre"
        )
        pieces = self._extract_field(
            block, "Liste de pièces à fournir"
        )
        coordonnees = self._extract_field(
            block, "Coordonnées"
        )

        if not incitation or not consistance:
            return None

        # Determine collection and generate ID
        collection = self._determine_collection(
            axe, organisation
        )
        if collection not in self.collection_counters:
            self.collection_counters[collection] = 0
        self.collection_counters[collection] += 1
        count = self.collection_counters[collection]
        doc_id = f"INC-{collection}{count:03d}"

        # Build full text for mapping
        full_text = " ".join([
            axe, incitation, consistance,
            cible, criteres
        ])

        # Extract organization details
        tel_match = re.search(
            r'(?:Tél?\s*:?\s*)([\d\s\-\+/]+)',
            coordonnees
        )
        web_match = re.search(
            r'((?:www\.|http)[^\s]+)', coordonnees
        )

        # Extract numeric conditions
        invest_min = self._extract_numeric_condition(
            criteres + " " + consistance,
            [
                r'investissement.*?(?:égal|supérieur).*?'
                r'(\d[\d\s\.]*)\s*(?:MDH|millions?)',
                r'(\d[\d\s\.]*)\s*(?:MDH|millions?).*?minimum'
            ]
        )
        ca_max = self._extract_numeric_condition(
            criteres + " " + cible,
            [
                r"chiffre d'affaires.*?(?:inférieur|ne dépassant).*?"
                r"(\d[\d\s\.]*)\s*(?:MDH|millions?)",
                r"CA.*?(?:inférieur|≤).*?"
                r"(\d[\d\s\.]*)\s*(?:MDH|millions?)"
            ]
        )

        # Build the document
        document = {
            "id": doc_id,
            "nom": incitation.strip(),
            "nom_court": self._shorten_name(incitation),
            "axe": axe.strip(),
            "type_incitation": self._determine_type(
                consistance, incitation
            ),
            "description_courte": (
                self._generate_short_description(
                    incitation, consistance
                )
            ),
            "description_complete": consistance.strip(),
            "avantages": self._extract_bullet_points(
                consistance
            ),
            "montant_ou_taux": self._extract_amounts(
                consistance
            ),
            "duree": self._extract_duration(consistance),
            "cible": {
                "tailles": self._extract_raw_sizes(cible),
                "secteurs": self._extract_raw_sectors(
                    cible, axe
                ),
                "profils_speciaux": (
                    self._extract_special_profiles(cible)
                )
            },
            "criteres_eligibilite": (
                self._extract_bullet_points(criteres)
            ),
            "conditions": {
                "investissement_min": (
                    invest_min * 1000000 if invest_min
                    else None
                ),
                "investissement_max": None,
                "ca_min": None,
                "ca_max": (
                    ca_max * 1000000 if ca_max
                    else None
                ),
                "anciennete_max_annees": (
                    self._extract_numeric_condition(
                        criteres,
                        [r'(\d+)\s*ans?\s*maximum']
                    )
                ),
                "export_min_pct": (
                    self._extract_numeric_condition(
                        criteres,
                        [r'(\d+)\s*%.*?export']
                    )
                ),
                "emplois_min": (
                    self._extract_numeric_condition(
                        criteres + " " + consistance,
                        [r'(\d+)\s*emplois?\s*(?:stables?|minimum)']
                    )
                )
            },
            "pieces_a_fournir": self._extract_pieces(pieces),
            "organisation": {
                "nom": (
                    organisation.split("\n")[0].strip()
                    if organisation else ""
                ),
                "telephone": (
                    tel_match.group(1).strip()
                    if tel_match else ""
                ),
                "site_web": (
                    web_match.group(1).strip()
                    if web_match else ""
                ),
                "adresse": ""
            },
            "modalites": modalites.strip() if modalites else "",
            "localisation_applicable": self._map_locations(
                full_text
            ),
            "tags": self._generate_tags(
                incitation, consistance, axe
            ),
            "secteurs_map": self._map_sectors(full_text),
            "tailles_map": self._map_sizes(cible),
            "mots_cles_recherche": self._generate_tags(
                incitation, consistance, axe
            )
        }

        return document

    # ---- Helper methods ----

    def _shorten_name(self, name: str) -> str:
        """Create abbreviated name."""
        short = name.strip()
        if len(short) > 60:
            short = short[:57] + "..."
        return short

    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text."""
        if not text:
            return []
        lines = text.split("\n")
        bullets = []
        for line in lines:
            cleaned = re.sub(
                r'^[\s\-\•\*\\]+', '', line
            ).strip()
            if cleaned and len(cleaned) > 10:
                bullets.append(cleaned)
        return bullets[:15]  # Cap at 15 items

    def _extract_amounts(self, text: str) -> str:
        """Extract monetary amounts and rates."""
        amounts = []
        patterns = [
            r'\d+[\s]*%',
            r'\d[\d\s\.]*\s*(?:MDH|DH|MAD|€|\$)',
            r'plafond[ée]?\s*(?:à|de)\s*[\d\s\.]+\s*(?:MDH|DH)',
        ]
        for p in patterns:
            matches = re.findall(p, text, re.IGNORECASE)
            amounts.extend(matches[:3])
        return "; ".join(amounts[:5]) if amounts else ""

    def _extract_duration(self, text: str) -> str:
        """Extract duration information."""
        patterns = [
            r'(\d+)\s*(?:ans?|années?|exercices?)',
            r'(\d+)\s*mois',
            r'permanent',
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return ""

    def _extract_raw_sizes(self, cible: str) -> List[str]:
        """Extract raw size mentions."""
        sizes = []
        for size, keywords in SIZE_MAPPING.items():
            for kw in keywords:
                if kw.lower() in cible.lower():
                    sizes.append(kw)
        return list(set(sizes)) if sizes else ["Non spécifié"]

    def _extract_raw_sectors(
        self, cible: str, axe: str
    ) -> List[str]:
        """Extract raw sector mentions."""
        text = (cible + " " + axe).lower()
        if "tous" in text and "secteur" in text:
            return ["Tous les secteurs"]
        sectors = []
        sector_words = [
            "industrie", "agriculture", "tourisme",
            "hôtellerie", "transport", "technologie",
            "BTP", "construction", "commerce",
            "pêche", "artisanat", "énergie"
        ]
        for s in sector_words:
            if s.lower() in text:
                sectors.append(s)
        return sectors if sectors else ["Non spécifié"]

    def _extract_special_profiles(
        self, cible: str
    ) -> List[str]:
        """Extract special target profiles."""
        profiles = []
        profile_keywords = {
            "MRE": ["MRE", "marocain résidant",
                     "résidant à l'étranger"],
            "Jeune entrepreneur": ["jeune", "porteur de projet"],
            "Femme entrepreneuse": ["femme"],
            "Auto-entrepreneur": ["auto-entrepreneur",
                                   "auto entrepreneur"],
            "Startup": ["startup", "start-up"],
            "Coopérative": ["coopérative"],
            "Exportateur": ["exportat"],
        }
        for profile, keywords in profile_keywords.items():
            for kw in keywords:
                if kw.lower() in cible.lower():
                    profiles.append(profile)
                    break
        return profiles


# ============================================================
# FILE OUTPUT
# ============================================================

def save_jsons(
    documents: List[Dict],
    output_dir: str = "incitations_json"
):
    """Save all documents as individual JSON files
    + one combined file."""

    os.makedirs(output_dir, exist_ok=True)

    # Individual files
    for doc in documents:
        filepath = os.path.join(
            output_dir, f"{doc['id']}.json"
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    # Combined file (for bulk loading)
    combined_path = os.path.join(
        output_dir, "_all_incitations.json"
    )
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    # Generate metadata/mapping files
    _generate_metadata(documents, output_dir)

    print(f"Saved {len(documents)} JSON files to {output_dir}/")
    print(f"Combined file: {combined_path}")


def _generate_metadata(
    documents: List[Dict], output_dir: str
):
    """Generate the 3 metadata mapping files."""

    # META-001: Sector → IDs
    sector_map = {}
    for doc in documents:
        for sector in doc["secteurs_map"]:
            if sector not in sector_map:
                sector_map[sector] = []
            sector_map[sector].append(doc["id"])

    with open(
        os.path.join(output_dir, "META-001_secteurs.json"),
        'w', encoding='utf-8'
    ) as f:
        json.dump(sector_map, f, ensure_ascii=False, indent=2)

    # META-002: Size → IDs
    size_map = {}
    for doc in documents:
        for size in doc["tailles_map"]:
            if size not in size_map:
                size_map[size] = []
            size_map[size].append(doc["id"])

    with open(
        os.path.join(output_dir, "META-002_tailles.json"),
        'w', encoding='utf-8'
    ) as f:
        json.dump(size_map, f, ensure_ascii=False, indent=2)

    # META-003: Location → IDs
    loc_map = {}
    for doc in documents:
        for loc in doc["localisation_applicable"]:
            if loc not in loc_map:
                loc_map[loc] = []
            loc_map[loc].append(doc["id"])

    with open(
        os.path.join(output_dir, "META-003_locations.json"),
        'w', encoding='utf-8'
    ) as f:
        json.dump(loc_map, f, ensure_ascii=False, indent=2)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Main execution: read MD, extract, save JSONs."""

    md_file = "incitations.md"  # Your MD file

    print(f"Reading {md_file}...")
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    print("Extracting incentives...")
    extractor = IncentiveExtractor(md_content)
    documents = extractor.parse()

    print(f"\nExtraction Summary:")
    print(f"  Total documents: {len(documents)}")

    # Count by collection
    collections = {}
    for doc in documents:
        col = doc["id"].split("-")[1][0]
        collections[col] = collections.get(col, 0) + 1

    for col, count in sorted(collections.items()):
        print(f"  Collection {col}: {count} documents")

    # Count by type
    types = {}
    for doc in documents:
        t = doc["type_incitation"]
        types[t] = types.get(t, 0) + 1

    print(f"\n  By type:")
    for t, count in sorted(types.items()):
        print(f"    {t}: {count}")

    print("\nSaving JSON files...")
    save_jsons(documents)

    print("\nDone!")


if __name__ == "__main__":
    main()