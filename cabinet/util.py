# cabinet/utils.py
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import dateparser

from datetime import datetime

def parse_french_date(date_str):
    mois_fr = {
        'janvier': '01', 'février': '02', 'fevrier': '02', 'mars': '03',
        'avril': '04', 'mai': '05', 'juin': '06', 'juillet': '07',
        'août': '08', 'aout': '08', 'septembre': '09', 'octobre': '10',
        'novembre': '11', 'décembre': '12', 'decembre': '12'
    }

    date_str = date_str.strip().lower()

    # Remplacer les mois français par leur numéro
    for mois, numero in mois_fr.items():
        if mois in date_str:
            date_str = re.sub(mois, numero, date_str)
            break

    # Maintenant on a quelque chose comme '14 03 2025'
    try:
        return datetime.strptime(date_str, "%d %m %Y").date()
    except ValueError:
        return None

import re
import dateparser

def extract_date(texte):
    # Recherche des dates au format JJ/MM/AAAA ou JJ mois AAAA
    pattern = r"(\d{2}/\d{2}/\d{4}|\d{1,2} [a-zéû]+ \d{4})"
    match = re.search(pattern, texte, re.IGNORECASE)
    if match:
        date_str = match.group(1)
        parsed = dateparser.parse(date_str, languages=['fr'])
        if parsed:
            return parsed.strftime('%d/%m/%Y')
    return None

import re
import dateparser

def extract_dates_from_text(texte):
    # Dictionnaire pour stocker les dates trouvées
    dates = {}

    # Liste des labels possibles et leur clé dans le dict
    labels = {
        'Date RC': 'date_rc',
        'Date CNSS': 'date_cnss',
        'Date contrat de bail': 'date_bail',
        'Date statut': 'date_statuts',
        'Date certificat negatif': 'date_certificat_negatif',
        'Date TP': 'date_tp',
        'Date BO': 'date_bo',
        'Date AL': 'date_al',
        'Date RQ': 'date_rq',
    }

    for label, key in labels.items():
        # Recherche de la date après le label, format jj/mm/aaaa ou jj mois aaaa
        pattern = fr"{label}\s*[:\-]?\s*(\d{{2}}/\d{{2}}/\d{{4}}|\d{{1,2}} [a-zéû]+ \d{{4}})"
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            parsed = dateparser.parse(match.group(1), languages=['fr'])
            if parsed:
                dates[key] = parsed.strftime('%d/%m/%Y')
    print("Dates extraites:", dates)  
    return dates


def extract_date_finale(texte):
    pattern = r"Fait à [A-Za-zÀ-ÖØ-öø-ÿ\s\-]+, le\s+(\d{1,2}\s+[a-zéû]+\s+\d{4})"
    matches = re.findall(pattern, texte, re.IGNORECASE)
    if matches:
        date_str = matches[-1]
        parsed = dateparser.parse(date_str, languages=['fr'])
        if parsed:
            return parsed.strftime('%d/%m/%Y')
    pattern_registre = r"DERNIÈRE MISE À JOUR DU REGISTRE\s*:\s*(\d{1,2}\s+[a-zéû]+\s+\d{4})"
    match = re.search(pattern_registre, texte, re.IGNORECASE)
    if match:
        date_str = match.group(1)
        parsed = dateparser.parse(date_str, languages=['fr'])
        if parsed:
            return parsed.strftime('%d/%m/%Y')
    return None


def extract_dates_with_context(texte, window=20):
    """
    Extrait toutes les dates avec un contexte de 'window' caractères avant/après.
    Renvoie une liste de tuples : (date_str, date_obj, contexte)
    """
    pattern = r"(\d{2}/\d{2}/\d{4}|\d{1,2} [a-zéû]+ \d{4})"
    results = []

    for match in re.finditer(pattern, texte, re.IGNORECASE):
        date_str = match.group(1)
        start = max(0, match.start() - window)
        end = min(len(texte), match.end() + window)
        contexte = texte[start:end]

        parsed = dateparser.parse(date_str, languages=['fr'])
        if parsed:
            results.append((date_str, parsed.strftime('%d/%m/%Y'), contexte.lower()))

    return results

def pick_date_by_keyword(dates_with_context, keywords):
    """
    Cherche dans les contextes des dates les mots-clés fournis (liste).
    Renvoie la première date dont le contexte contient un des mots-clés.
    Si aucune trouvée, renvoie la première date (ou None si vide).
    """
    keywords = [k.lower() for k in keywords]

    for _, date_fmt, contexte in dates_with_context:
        if any(keyword in contexte for keyword in keywords):
            return date_fmt

    return dates_with_context[0][1] if dates_with_context else ""



    


import re

def extract_rc_number(text):
    # Recherche plusieurs formats possibles, par exemple :
    # "Numéro RC : 123456789", "N° RC-123456789", "RC n° 123456789"
    patterns = [
        r'Num[eé]ro\s+RC\s*[:\-]?\s*(\d{4,})',
        r'N°\s*RC\s*[:\-]?\s*(\d{4,})',
        r'RC\s*n°\s*[:\-]?\s*(\d{4,})',
        r'Certificat\s+RC\s*[:\-]?\s*(\d{4,})',
        r'RC\s*[:\-]?\s*(\d{4,})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None



def extract_cnss_number(text):
    match = re.search(r'\bCNSS\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    return match.group(1) if match else ''

def extraire_infos_tva_depuis_pdf(pdf_path):
    mois_mapping = {
        "janvier": "jan", "février": "fev", "mars": "mars", "avril": "avril",
        "mai": "mai", "juin": "juin", "juillet": "juillet", "août": "aout",
        "septembre": "sep", "octobre": "oct", "novembre": "nov", "décembre": "dec"
    }
    trimestres = {"1er trimestre": "t1", "2ème trimestre": "t2", "3ème trimestre": "t3", "4ème trimestre": "t4"}

    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)

    annee = None
    champs = {val: False for val in mois_mapping.values()}
    champs.update({val: False for val in trimestres.values()})

    for line in text.splitlines():
        line_lower = line.lower()
        if "année" in line_lower:
            for token in line.split():
                if token.isdigit() and len(token) == 4:
                    annee = int(token)
        for label, champ in mois_mapping.items():
            if f"{label} : déclaration effectuée" in line_lower:
                champs[champ] = True
        for label, champ in trimestres.items():
            if label in line_lower and "déclaration effectuée" in line_lower:
                champs[champ] = True

    return annee, champs


import re
from PyPDF2 import PdfReader

def extraire_infos_identifiants(pdf_path):
    reader = PdfReader(pdf_path)
    texte = "\n".join([page.extract_text() or '' for page in reader.pages])
    print(" Texte brut extrait :", texte)

    texte = texte.replace('\xa0', ' ')
    texte = texte.replace('’', "'")
    texte = texte.replace('：', ':')
    texte = re.sub(r'\s+', ' ', texte)

    infos = {}

    # IF
    match_if = re.search(r'Identifiant\s+Fiscal\s*(?:\(IF\))?\s*[:\-]?\s*(\d{5,})', texte, re.IGNORECASE)
    if not match_if:
        match_if = re.search(r'identifiée?.*?\bpar\b.*?(\d{5,})', texte, re.IGNORECASE)
    if match_if:
        infos['if_identifiant'] = match_if.group(1)

    # ICE
    match_ice = re.search(r'ICE\s*[: ]\s*(\d{10,})', texte)
    if match_ice:
        infos['ice'] = match_ice.group(1)

    # TP
    match_tp = re.search(
        r'(?i)(?:num[eé]ro\s+de\s+)?taxe\s+professionnelle\s*(?:\(TP\))?\s*[:\-]?\s*(\d{6,})|TP\s*[:\-]?\s*(\d{6,})',
        texte
    )
    if match_tp:
        infos['tp'] = match_tp.group(1) if match_tp.group(1) else match_tp.group(2)


    # RC
    match_rc = re.search(r'RC\s*[: ]\s*(\d+)', texte)
    if match_rc:
        infos['rc'] = match_rc.group(1)

    # CNSS
    match_cnss = re.search(r'CNSS\s*[: ]\s*(\d+)', texte)
    if match_cnss:
        infos['cnss'] = match_cnss.group(1)

   # Dénomination demandée
    match_denom = re.search(
        r'(?:Dénomination|Raison)\s+(?:sociale|demandée)?\s*[:\-]?\s*([A-Z0-9\- ]+)',
        texte,
        re.IGNORECASE
    )
    if match_denom:
        denom = match_denom.group(1).strip()
        # Supprimer une éventuelle forme juridique à la fin (SARL, SA, SNC, etc.)
        forme_juridique_regex = r'\b(SARL|S\.?A\.?|SA|SNC|SAS|SCOP|GIE|SCA|SCI|SCM|SCS|SCP)\b\.?$'
        denom = re.sub(forme_juridique_regex, '', denom, flags=re.IGNORECASE).strip()
        infos['denomination'] = denom



    # Forme juridique
    match_forme = re.search(
        r'\b(SARL|S\.A\.?R\.?L|SA|S\.A\.|SAS|S\.A\.S|SNC|S\.N\.C|Société à Responsabilité Limitée|Société Anonyme|Société en Nom Collectif|Société en Commandite)\b',
        texte,
        re.IGNORECASE
    )

    if match_forme:
        forme = match_forme.group(1).upper().replace('.', '')
        if 'SARL' in forme:
            infos['forme_juridique'] = 'SARL'
        elif 'SA' in forme:
            infos['forme_juridique'] = 'SA'
        elif 'SAS' in forme:
            infos['forme_juridique'] = 'SAS'
        elif 'SNC' in forme:
            infos['forme_juridique'] = 'SNC'
        else:
            infos['forme_juridique'] = forme


    # Gérant principal (supporte "gérée par", "gré par", majuscules accentuées et noms composés)
    match_gerant = re.search(
        r"La société est gr[ée]{1,2} par\s*[:\-]?\s*(Madame|Monsieur)\s+([A-ZÉÈÀÙÂÊÎÔÛÇ][a-zéèàùâêîôûç\-']+(?:\s+[A-ZÉÈÀÙÂÊÎÔÛÇ][a-zéèàùâêîôûç\-']+)+)",
        texte,
        re.IGNORECASE
    )

    if match_gerant:
        civilite = match_gerant.group(1).capitalize()
        nom_gerant = match_gerant.group(2).strip()
        infos['gerant'] = f"{civilite} {nom_gerant.title()}"

    elif 'gerant' not in infos:
        # Nouveau cas : "Le Gérant : Mehdi EL FASSI"
        match_simple_gerant = re.search(
            r"Le\s+Gérant\s*[:\-]?\s*([A-Z][a-zéèàùâêîôûç\-']+(?:\s+[A-Z][A-Z\-']+)+)",
            texte,
            re.IGNORECASE
        )
        if match_simple_gerant:
            nom_gerant = match_simple_gerant.group(1).strip()
            infos['gerant'] = nom_gerant.title()

        else:
            # Cas Président Directeur Général
            match_pdg = re.search(
                r'(?:Sont nommés membres.*?[\n\r]+)?[•\-●▪️\*\s]*([A-Z][A-Za-zÉÈÀÙÂÊÎÔÛÇç\-\' ]+?),\s*Président\s+Directeur\s+Général',
                texte,
                re.IGNORECASE | re.DOTALL
            )
            if match_pdg:
                nom_pdg = match_pdg.group(1).strip()
                infos['gerant'] = nom_pdg.title()










    match_mobile = re.search(r'(?:Téléphone mobile|Mobile)\s*[:\-]?\s*(\+?\d[\d\s]+)', texte, re.IGNORECASE)
    if match_mobile:
        infos['telephone_mobile'] = match_mobile.group(1).strip()

    # Téléphone fixe
    match_fixe = re.search(r'(?:Téléphone fixe|Fixe)\s*[:\-]?\s*(\+?\d[\d\s]+)', texte, re.IGNORECASE)
    if match_fixe:
        infos['telephone_fixe'] = match_fixe.group(1).strip()

    match_telephone = re.search(r'Téléphone\s*[:\-]?\s*(\+?\d[\d\s]+)', texte, re.IGNORECASE)
    if match_telephone:
        infos['telephone'] = match_telephone.group(1).strip()

    match_email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', texte)
    if match_email:
        infos['email'] = match_email.group(0)

    # Date de création
    dates_trouvees = re.findall(r'\d{1,2} [a-zéû]+ \d{4}', texte, re.IGNORECASE)

    # Cherche les dates précédées de mots clés pertinents
    match_creation = re.search(r"(date de (création|constitution|immatriculation))\s*[:\-]?\s*(\d{1,2} [a-zéû]+ \d{4})", texte, re.IGNORECASE)
    if match_creation:
        date_str = match_creation.group(3)
        parsed = dateparser.parse(date_str, languages=['fr'])
        if parsed:
            infos['date_creation'] = parsed.strftime('%d/%m/%Y')
    else:
        # Fallback prudent — éviter les dates comme 2034 (fin de bail par ex)
        for d in dates_trouvees:
            if "fin" in texte.lower() or "expire" in texte.lower() or "se terminant" in texte.lower():
                continue  #  ignorer les dates de fin
            parsed = dateparser.parse(d, languages=['fr'])
            if parsed and parsed.year <= 2025:  # ou tout seuil raisonnable
                infos['date_creation'] = parsed.strftime('%d/%m/%Y')
                break


    # Branche d'activité (améliorée pour listes à puces, multi-lignes, nettoyage adresse)
    # match_branche = re.search(
    #     r'(activité déclarée|activités?)\s*[:\-]?\s*(.+?)(?=(adresse|remarque|cnss|téléphone|email|e-mail|courriel|site|capital|rc|forme juridique|durée|objet|article|statut|siege|numéro|est affiliée|cette autorisation|dans le respect|$))',
    #     texte,
    #     re.IGNORECASE | re.DOTALL
    # )

    # if match_branche:
    #     branche = match_branche.group(2).strip()

    #     # Nettoyage avancé :
    #     # - Retire les puces, tirets, caractères parasites
    #     # - Supprime tout ce qui suit les mots-clés administratifs
    #     branche = re.sub(r'[•·●▪️\-–—]+\s*', '\n• ', branche)  # harmonise les puces
    #     branche = re.sub(r'\s*(est affiliée|cette autorisation|remarque|dans le respect).*$', '', branche, flags=re.IGNORECASE | re.DOTALL)

    #     branche = branche.strip().strip(":;.,")

    #     # Remplacer plusieurs lignes vides ou espaces répétées
    #     branche = re.sub(r'\n+', '\n', branche)
    #     branche = re.sub(r'[ \t]+', ' ', branche)

    #     infos['branche'] = branche
 

    match_branche = re.search(
        r'(activité déclarée|activités?)\s*[:\-]?\s*(.+?)(?=(adresse|remarque|cnss|téléphone|email|e-mail|courriel|site|capital|rc|forme juridique|durée|objet|article|statut|siege|numéro|est affiliée|cette autorisation|dans le respect|$))',
        texte,
        re.IGNORECASE | re.DOTALL
    )

    if match_branche:
        branche = match_branche.group(2).strip()
        # Correction générique des mots coupés par erreur, ex: "Dévelop pement"
        corrections_connues = {
            "Dévelop pement": "Développement",
            "dévelop pement": "développement",
            "dé veloppement": "développement",
            "Infor matique": "Informatique",
            "logic iels": "logiciels",
            "Multim edia": "Multimedia",
            "Numéri ques": "Numériques",
            "Cyber sécurité": "Cybersécurité",
            "Transfor mation": "Transformation",
            "arti ficielle": "artificielle",
            "intel ligence": "intelligence",
            "big data": "big data",
            "tech nologie": "technologie",
            "for mation": "formation",
            "cloud computing": "cloud computing"
        }

        # Appliquer les corrections connues
        for coupure, correction in corrections_connues.items():
            branche = branche.replace(coupure, correction)
        # Supprime tous les caractères de puces typographiques et parasites invisibles
        branche = re.sub(r'[•·●▪️■♦☑️☐✓▶►➤➔➣→←⇒⇨‣∙●◦■◆●–—−‒‐•▪️]', '', branche)

        # Supprime les espaces multiples ou restes inutiles
        branche = re.sub(r'\s{2,}', ' ', branche)
        branche = branche.strip(":;., \n")



        #  Corrige les mots collés sans espace après "de", "et"
        branche = re.sub(r'\b(de|et)([a-zéèàùâêîôûç]{2,})\b', r'\1 \2', branche, flags=re.IGNORECASE)
        branche = re.sub(
            r'(\b\w{3,7})\s+(\w{3,})',
            lambda m: m.group(1) + m.group(2) if (m.group(1) + m.group(2)).lower() in [
                'developpement', 'logiciels', 'hebergement', 'cloud', 'numeriques',
                'conseil', 'multimedia', 'technologie', 'informatique', 'cybersecurite',
                'intelligenceartificielle', 'bigdata', 'formation', 'communication'
            ] else m.group(0),
            branche
        )


        #  Nettoie les caractères parasites (puces, tirets, etc.)
        branche = re.sub(r'[•·●▪️\-\–—]+', '', branche)

        #  Nettoie les espaces multiples, ponctuations en trop
        branche = re.sub(r'\s{2,}', ' ', branche)
        branche = branche.strip(":;., \n")

        infos['branche'] = branche





        # Secteur (dérivé)
        branche_lc = branche.lower()

        if any(kw in branche_lc for kw in ['logiciel', 'informatique', 'système d\'information', 'it', 'numérique', 'digital']):
            infos['secteur'] = "Technologies de l'information"
        elif any(kw in branche_lc for kw in ['construction', 'chantier', 'bâtiment', 'génie civil']):
            infos['secteur'] = "BTP"
        elif any(kw in branche_lc for kw in ['transport', 'logistique', 'livraison']):
            infos['secteur'] = "Transport"
        elif any(kw in branche_lc for kw in ['agriculture', 'élevage', 'produits agricoles', 'ferme']):
            infos['secteur'] = "Agriculture"
        elif any(kw in branche_lc for kw in ['commerce', 'achat', 'vente', 'distribution', 'import', 'export']):
            infos['secteur'] = "Commerce"
        elif any(kw in branche_lc for kw in ['restauration', 'restaurant', 'traiteur', 'café']):
            infos['secteur'] = "Restauration"
        elif any(kw in branche_lc for kw in ['éducation', 'formation', 'enseignement']):
            infos['secteur'] = "Éducation"
        elif any(kw in branche_lc for kw in ['finance', 'comptabilité', 'audit', 'banque', 'assurance']):
            infos['secteur'] = "Finance"
        elif any(kw in branche_lc for kw in ['immobilier', 'location', 'bail', 'gestion immobilière']):
            infos['secteur'] = "Immobilier"
        elif any(kw in branche_lc for kw in ['textile', 'habillement', 'confection']):
            infos['secteur'] = "Textile"
        elif any(kw in branche_lc for kw in ['industrie', 'production', 'manufacture']):
            infos['secteur'] = "Industrie"
        elif any(kw in branche_lc for kw in ['santé', 'clinique', 'pharmacie', 'médical']):
            infos['secteur'] = "Santé"
        elif any(kw in branche_lc for kw in ['tourisme', 'voyage', 'hôtel', 'hébergement']):
            infos['secteur'] = "Tourisme"
        else:
            infos['secteur'] = "Autres"




    # TVA : fréquence de déclaration
    # --- Détection du régime de TVA ---
    texte_tva = texte.lower()

    if 'régime du réel simplifié' in texte_tva or 'reel simplifie' in texte_tva or 'trimestrielle' in texte_tva:
        infos['tva'] = 'TRIMESTRIELLE'
    elif 'régime du réel normal' in texte_tva or 'reel normal' in texte_tva or 'mensuelle' in texte_tva:
        infos['tva'] = 'MENSUELLE'
    else: 
        infos['tva'] = 'EXONEREE'
    






    # CIN
    match_cin = re.search(r'CIN\s*[:\-]\s*([A-Z]{1,2}\d{5,})', texte)
    if match_cin:
        infos['cin'] = match_cin.group(1).strip()

    # Adresse
    match_adresse = re.search(
        r'Siège social\s*[:\-]?\s*(.+?)(?=\s*(Objet|Capital|Durée|Article|Activité|activité|Adresse|RC|Téléphone|E-mail|Courriel|Forme juridique|Statut))',
        texte,
        re.IGNORECASE | re.DOTALL
    )
    if match_adresse:
        adresse = match_adresse.group(1).strip()
        # Ajouter le caractère de puce spéciale `` (\u2022 ou copier directement)
        adresse = re.split(r'[•·●▪️\-\–—‒―—–‐−‾\-–—●▪️•·`•´’‘”“„"\'`¨~°<>†‡※⁂⁑⁜⁘⸗❖◆◇■□▣▤▥▦▧▨▩◘◙◦☛☞☚☜→←↑↓↔↕↨↵↩↪↺↻⇄⇅⇆⇇⇈⇉⇊⇋⇌⇒⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪]|\u2022|', adresse)[0].strip()
        infos['adresse'] = adresse
    
    






    return infos






import re
import fitz  # PyMuPDF

def extraire_periode_depuis_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    texte = "\n".join(page.get_text() for page in doc)

    # Recherche période : "01/06/2025 au 30/06/2025" ou "01/04/2025 au 30/06/2025"
    match = re.search(r"(\d{2})/(\d{2})/(\d{4})\s+au\s+(\d{2})/(\d{2})/(\d{4})", texte)
    if not match:
        return None, {}

    mois_debut = int(match.group(2))
    annee = int(match.group(3))
    mois_fin = int(match.group(5))

    duree = mois_fin - mois_debut + 1

    # Champs possibles
    champs = {m: False for m in [
        'jan', 'fev', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'aout', 'sep', 'oct', 'nov', 'dec',
        't1', 't2', 't3', 't4'
    ]}

    mois_map = {
        1: "jan", 2: "fev", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
        7: "juillet", 8: "aout", 9: "sep", 10: "oct", 11: "nov", 12: "dec"
    }

    trimestre_map = {
        (1, 3): 't1',
        (4, 6): 't2',
        (7, 9): 't3',
        (10, 12): 't4'
    }

    if duree == 1:
        # déclaration mensuelle
        if mois_debut in mois_map:
            champs[mois_map[mois_debut]] = True
    elif duree == 3:
        # déclaration trimestrielle
        for (debut, fin), champ in trimestre_map.items():
            if mois_debut == debut and mois_fin == fin:
                champs[champ] = True
                break
    else:
        # autre cas : possible déclaration annuelle ou erronée, gérer selon besoin
        pass

    return annee, champs


def enregistrer_suivi_tva(dossier, texte_extrait):
    infos = extraire_infos_tva_depuis_pdf(texte_extrait)
    annee_actuelle = datetime.now().year

    suivi, created = SuiviTVA.objects.get_or_create(
        dossier=dossier,
        annee=annee_actuelle
    )

    for champ, valeur in infos.items():
        setattr(suivi, champ, valeur)

    suivi.save()

def extract_text_from_pdf(file):
    file.seek(0)
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    text=""
    for page in pdf:
        txt = page.get_text()
        if txt.strip():
            text += txt
        else:
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes()))
            text += pytesseract.image_to_string(img)
    return text


def extraire_infos_dossier(text):
    """Extrait les champs du dossier à partir du texte OCR."""
    return {
        'denomination': re.search(r"(?:Dénomination|Entreprise)[:\s]+(.+)", text).group(1).strip() if re.search(r"(?:Dénomination|Entreprise)[:\s]+(.+)", text) else None,
        'forme_juridique': re.search(r"(Forme juridique|Statut)[:\s]+(.+)", text).group(2).strip() if re.search(r"(Forme juridique|Statut)[:\s]+(.+)", text) else None,
        'adresse': re.search(r"(Adresse)[:\s]+(.+)", text).group(2).strip() if re.search(r"(Adresse)[:\s]+(.+)", text) else None,
        'if_identifiant': re.search(r"(IF|Identifiant Fiscal)[:\s]+(\d+)", text).group(2).strip() if re.search(r"(IF|Identifiant Fiscal)[:\s]+(\d+)", text) else None,
        'ice': re.search(r"(ICE|Identifiant Commun)[:\s]+(\d+)", text).group(2).strip() if re.search(r"(ICE|Identifiant Commun)[:\s]+(\d+)", text) else None,
        'rc': re.search(r"(RC|Registre Commerce)[:\s]+(\d+)", text).group(2).strip() if re.search(r"(RC|Registre Commerce)[:\s]+(\d+)", text) else None,
        'email': re.search(r"Email[:\s]+([\w\.-]+@[\w\.-]+)", text).group(1).strip() if re.search(r"Email[:\s]+([\w\.-]+@[\w\.-]+)", text) else None,
        'telephone': re.search(r"Tél(?:éphone)?[:\s]+([\d\s]+)", text).group(1).strip() if re.search(r"Tél(?:éphone)?[:\s]+([\d\s]+)", text) else None,
        'gerant': re.search(r"Gérant[:\s]+(.+)", text).group(1).strip() if re.search(r"Gérant[:\s]+(.+)", text) else None,
    }
