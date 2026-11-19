from html import escape
from analyseur_lexical import analyse

table_analyse={
    ('Programme','main'): ['main','(',')','{','liste_declarations','liste_instructions','}'],

    ('liste_declarations','int'): ['une_declaration','liste_declarations'],
    ('liste_declarations','float'): ['une_declaration','liste_declarations'],
    ('liste_declarations','id'): [],
    ('liste_declarations','if'): [],
    ('liste_declarations','}'): [],

    ('une_declaration','int'): ['type','id'],
    ('une_declaration','float'): ['type','id'],

    ('liste_instructions','id'): ['une_instruction','liste_instructions'],
    ('liste_instructions','if'): ['une_instruction','liste_instructions'],
    ('liste_instructions','}'): [],

    ('une_instruction','id'): ['affectation'],
    ('une_instruction','if'): ['test'],

    ('type','int'): ['int'],
    ('type','float'): ['float'],

    ('affectation','id'): ['id','=','nombre',';'],

    ('test','if'):['if','condition','une_instruction','else','une_instruction',';'],

    ('condition','id'):['id','operateur','nombre'],

    ('operateur','<'): ['<'],
    ('operateur','>'): ['>'],
    ('operateur','='): ['=']
}

def convertir_token(token, lexeme):
    if token == "id" and lexeme in Mots_cles:
        return lexeme

    elif token == "AFFECTATION":
        return "="

    elif token == "SEPARATEUR":
        return lexeme

    elif token == "OPERATEUR":
        return lexeme

    else:
        return token

Mots_cles=["main","int","float","if","else"]

non_terminaux=["Programme","liste_declarations","une_declaration","liste_instructions","une_instruction","affectation","test","condition","operateur","type"]

class Noeud:
    def __init__(self,symbole,valeur=None):
        self.symbole=symbole
        self.valeur= valeur
        self.enfants=[]

def afficher_arbre(noeud, niveau=0):
    if noeud.valeur is not None:
        print("  " * niveau + noeud.symbole + " : " + noeud.valeur)
    else:
        print("  " * niveau + noeud.symbole)

    for enfant in noeud.enfants:
        afficher_arbre(enfant, niveau + 1)


#  AFFICHAGE HTML

def noeud_en_html(noeud, niveau=0):
    couleur = "niv" + str(niveau % 6)
    if noeud.symbole in non_terminaux:
        etiquette = "<span class='nt " + couleur + "'>" + escape(noeud.symbole) + "</span>"
    else:
        texte = escape(noeud.symbole)
        if noeud.valeur is not None and noeud.valeur != noeud.symbole:
            texte += " : " + escape(noeud.valeur)
        etiquette = "<span class='t " + couleur + "'>" + texte + "</span>"

    html = "<li>" + etiquette
    if noeud.enfants:
        html += "<ul>"
        for enfant in noeud.enfants:
            html += noeud_en_html(enfant, niveau + 1)
        html += "</ul>"
    elif noeud.symbole in non_terminaux:
        html += "<ul><li><span class='eps'>ε</span></li></ul>"
    html += "</li>"
    return html

def regle_en_html(gauche, droite):
    if droite:
        corps = " ".join(escape(x) for x in droite)
    else:
        corps = "ε"
    return "<li><span class='gauche'>" + escape(gauche) + "</span> → " + corps + "</li>"

def generer_html(racine, programme, tokens, regles, erreur, chemin="resultat.html"):
    css = """
    body { font-family: Georgia, serif; background: #f3f5f8; color: #1b2430; padding: 24px; }
    h2 { font-size: 1.1rem; margin: 28px 0 10px 0; }

    .src { background: #fff; border: 1px solid #b9c3d0; border-radius: 6px;
           padding: 10px 14px; font-family: monospace; margin: 0; }
    .pastilles { display: flex; flex-wrap: wrap; gap: 8px; }
    .pastille { background: #fff; border: 1px solid #b9c3d0; border-radius: 6px;
                padding: 2px 8px; font-family: monospace; font-size: 0.9rem; }
    .pastille small { color: #5d6b7c; margin-right: 6px; }

    .arbre { overflow-x: auto; padding-bottom: 16px; }
    .arbre > ul { width: max-content; min-width: 100%; padding-top: 0; }

    ul { display: flex; justify-content: center; list-style: none;
         padding: 20px 0 0 0; margin: 0; position: relative; }
    li { text-align: center; position: relative; padding: 20px 6px 0 6px; }

    /* traits horizontaux et verticaux au-dessus de chaque nœud */
    li::before, li::after { content: ""; position: absolute; top: 0; right: 50%;
        width: 50%; height: 20px; border-top: 1px solid #b9c3d0; }
    li::after { right: auto; left: 50%; border-left: 1px solid #b9c3d0; }

    /* nœud unique : seulement le trait vertical du parent */
    li:only-child::before, li:only-child::after { display: none; }
    li:only-child { padding-top: 0; }

    /* extrémités : pas de trait qui dépasse */
    li:first-child::before, li:last-child::after { border: 0 none; }
    li:last-child::before { border-right: 1px solid #b9c3d0; border-radius: 0 6px 0 0; }
    li:first-child::after { border-radius: 6px 0 0 0; }

    /* trait vertical entre un parent et la rangée de ses enfants */
    ul ul::before { content: ""; position: absolute; top: 0; left: 50%;
        border-left: 1px solid #b9c3d0; height: 20px; }

    /* la racine n'a pas de parent : pas de trait au-dessus */
    .arbre > ul > li { padding-top: 0; }
    .arbre > ul > li::before, .arbre > ul > li::after { display: none; }

    /* nœuds : la couleur vient du niveau (variables --c et --bg) */
    .nt, .t { padding: 2px 10px; border-radius: 6px; font-family: monospace;
              display: inline-block; white-space: nowrap;
              color: var(--c); background: var(--bg); }
    .nt { border: 1px solid var(--c); }

    .niv0 { --c: #2f5da8; --bg: #e8effa; }
    .niv1 { --c: #17694f; --bg: #e2f4ec; }
    .niv2 { --c: #a4561a; --bg: #fbeedd; }
    .niv3 { --c: #6b44a8; --bg: #efe8fa; }
    .niv4 { --c: #a73a62; --bg: #fae6ee; }
    .niv5 { --c: #1b6f7a; --bg: #e0f3f5; }

    .regles { font-family: monospace; font-size: 0.9rem; line-height: 1.8; }
    .regles .gauche { color: #2f5da8; }
    .regles li { text-align: left; padding: 0; }
    .regles li::before, .regles li::after { display: none; }

    .statut { border-radius: 6px; padding: 10px 14px; font-family: monospace; margin-top: 12px; }
    .ok { background: #e2f4ec; border: 1px solid #17694f; color: #17694f; }
    .erreur { background: #fdeceb; border: 1px solid #b3261e; color: #b3261e; }

    .eps { color: #8793a3; border: 1px dashed #b9c3d0; padding: 2px 10px;
           border-radius: 6px; font-family: monospace; display: inline-block; }
    """
    page = "<!doctype html><html><head><meta charset='utf-8'><title>Arbre syntaxique</title>"
    page += "<style>" + css + "</style></head><body>"
    page += "<h1>Arbre syntaxique</h1>"

    page += "<h2>Programme analysé</h2>"
    page += "<pre class='src'>" + escape(programme) + "</pre>"
    if erreur:
        page += "<div class='statut erreur'>Erreur syntaxique : " + escape(erreur) + "</div>"
    else:
        page += "<div class='statut ok'>Programme syntaxiquement correct</div>"

    page += "<h2>Tokens</h2><div class='pastilles'>"
    for token, lexeme in tokens:
        page += "<span class='pastille'><small>" + escape(token) + "</small>" + escape(lexeme) + "</span>"
    page += "</div>"

    if racine is not None:
        page += "<h2>Arbre</h2>"
        page += "<div class='arbre'><ul>" + noeud_en_html(racine) + "</ul></div>"

    page += "<h2>Règles appliquées</h2><ol class='regles'>"
    for gauche, droite in regles:
        page += regle_en_html(gauche, droite)
    page += "</ol>"

    page += "</body></html>"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(page)


# ANALYSE SYNTAXIQUE 

def analyse_syntaxique(tokens):
    racine=Noeud("Programme")
    pile=["$","Programme"]
    pile_noeuds=[None, racine]
    position=0
    regles=[]
    while len(tokens)>position and len(pile)>1:
        sommet=pile[-1]
        noeud=pile_noeuds[-1]
        token, lexeme=tokens[position]
        token=convertir_token(token,lexeme)

        if sommet in non_terminaux:
            cle=(sommet,token)
            if cle in table_analyse:
                action=table_analyse[cle]
                regles.append((sommet, action))
                pile.pop()
                pile_noeuds.pop()
                nouveaux_noeuds=[]

                for symbole in action:
                    enfant= Noeud(symbole)
                    noeud.enfants.append(enfant)
                    nouveaux_noeuds.append(enfant)

                for enfant in reversed(nouveaux_noeuds):
                    pile.append(enfant.symbole)
                    pile_noeuds.append(enfant)
            else:
                return None, regles, "aucune règle pour " + sommet + " avec le symbole " + lexeme
        else:
            if sommet ==token:
                noeud.valeur=lexeme
                pile.pop()
                pile_noeuds.pop()
                position+=1
            else:
                return None, regles, sommet + " attendu, mais " + lexeme + " trouvé"

    if len(pile)>1:
        attendus = [x for x in reversed(pile[1:]) if x not in non_terminaux]
        if attendus:
            return None, regles, "fin du programme inattendue, " + attendus[0] + " attendu"
        return None, regles, "fin du programme inattendue"
    if position!=len(tokens):
        return None, regles, "symbole inattendu après la fin du programme : " + tokens[position][1]

    return racine, regles, None


if __name__ == "__main__":
    programme = "main() {int x x=5;}"
    #programme = "main() {int x float y x=5; if x<3 y=1; else y=2; ;}"
    #programme = "{x=5; int y}"
    tokens=analyse(programme)
    arbre, regles, erreur = analyse_syntaxique(tokens)
    if erreur:
        print("Erreur syntaxique :", erreur)
    else:
        print("Programme syntaxiquement correct")
        afficher_arbre(arbre)
    generer_html(arbre, programme, tokens, regles, erreur)
