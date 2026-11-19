def reconnaitre_identificateur(mot):
    etat = 0
    for caractere in mot:
        if etat == 0:
            if caractere.isalpha():
                etat = 1
            else:
                return False
        elif etat == 1:
            if caractere.isalnum():
                etat = 1
            else:
                return False
    return etat == 1
 
 
def reconnaitre_nombre(nb):
    etat = 0
    for caractere in nb:
        if etat == 0:
            if caractere.isdigit():
                etat = 1
            else:
                return False
        elif etat == 1:
            if caractere.isdigit():
                etat = 1
            else:
                return False
    return etat == 1
 
 
def reconnaitre_operateur(op):
    etat = 0
    for caractere in op:
        if etat == 0:
            if caractere in {"+", "-", "*", "/","<",">"}:
                etat = 1
            else:
                return False
        else:
            return False
    return etat == 1
 
 
def reconnaitre_affectation(aff):
    etat = 0
    for caractere in aff:
        if etat == 0:
            if caractere == "=":
                etat = 1
            else:
                return False
        else:
            return False
    return etat == 1
 
 
def reconnaitre_separateur(sep):
    etat = 0
    for caractere in sep:
        if etat == 0:
            if caractere in {"(", ")", ";","{","}"}:
                etat = 1
            else:
                return False
        else:
            return False
    return etat == 1
 
 
#  PARTIE 4 : analyseur lexical
 
# chaque automate est associe au nom de son token
CATEGORIES = [
    (reconnaitre_identificateur, "id"),
    (reconnaitre_nombre, "nombre"),
    (reconnaitre_operateur, "OPERATEUR"),
    (reconnaitre_affectation, "AFFECTATION"),
    (reconnaitre_separateur, "SEPARATEUR"),
]
 
 
def categorie(lexeme):
    #Teste les automates un par un, retourne le nom du token.
    for automate, nom in CATEGORIES:
        if automate(lexeme):
            return nom
    return "ERREUR LEXICALE"
 
 
def analyse(chaine):
    tokens = []          # liste de couples (token, lexeme)
    i = 0
    n = len(chaine)
    while i < n:
        c = chaine[i]
 
        # espaces, tabulations (et retours a la ligne) ignores
        if c in " \t\n":
            i += 1
 
        # bloc de lettres/chiffres colles = un seul lexeme
        elif c.isalnum():
            debut = i
            while i < n and chaine[i].isalnum():
                i += 1
            lexeme = chaine[debut:i]
            tokens.append((categorie(lexeme), lexeme))
 
        # tout autre caractere = un lexeme a lui seul
        else:
            tokens.append((categorie(c), c))
            i += 1
 
    return tokens


 