"""
Auteur : Charlotte Nachtegael
Date : Novembre 2019
But : Implémenter le jeu slideways avec une IA basique adverse
"""
import os
import random
from copy import deepcopy

JOUEUR_HUMAN = 1
JOUEUR_AI = 2

COLONNES = ['A', 'B', 'C', 'D']
LIGNES = ['1', '2', '3', '4']
SIGNES = ['-', '+']
SYMBOLES = ['_', 'X', 'O']

TAILLE = 4

DRAW = 0
WIN = 1
LOSS = -1


def afficher(plateau, decalage):
    """
        Affiche le plateau de jeu avec les coups joués par les joueurs et les numéros et lettre pour les lignes et
        colonnes
        :param plateau: liste de liste, 0 pour vide, 1 ou 2 pour joueur
        :param decalage: list d'entiers, représentent le décalage des lignes du plateau
        :return: None
    """
    s = '\n'
    for i in range(TAILLE - 1, -1, -1):
        s += ' ' + str(i + 1) + '  '
        for j in range(-3, 7):
            if -1 < j - decalage[i] < TAILLE:
                s += "{:3}".format(SYMBOLES[plateau[i][j - decalage[i]]])
            else:
                s += "{:>3}".format(" ")
        s += '\n\n'
    s += '{:>13}{:3}{:3}{:3}{:3}\n\n'.format(" ", "A", "B", "C", "D")
    # os.system('clear')
    print(s)


def nouveau_plateau():
    """
        Crée le plateau de jeu
        :return: liste de liste de dimension 4x4 contenant des 0 et une liste de 4 0
    """
    plateau = []
    for i in range(TAILLE):
        plateau.append([0] * TAILLE)
    decalage = [0] * TAILLE
    return plateau, decalage


def mouvements_valides(plateau, decalage, dernier_coup, joueur):
    """
    Permet d'avoir la liste de tous les mouvements valides
    :param plateau: liste de liste, 0 pour vide, 1 ou 2 pour joueur ou AI
    :param decalage: list d'entiers, représentent le décalage des lignes du plateau
    :param dernier_coup: string de deux caractères, dernier coup joué
    :param joueur: entier, 1 ou 2
    :return: list des mouvements valides sans le dernier coup joué ou le
    mouvement de décalage opposé au dernier coup joué
    """
    mouvements = [col + ligne for col in COLONNES for ligne in LIGNES]
    decal = [ligne + sign for ligne in LIGNES for sign in SIGNES]

    if dernier_coup is not None:

        # retire mouvement du joueur
        for mouvement in mouvements:
            i = int(mouvement[1]) - 1
            j = COLONNES.index(mouvement[0])
            if plateau[i][j] == joueur:
                mouvements.remove(mouvement)

        # retire mouvement joué au dernier tour
        if dernier_coup in mouvements:
            mouvements.remove(dernier_coup)
        else:
            decal.remove(dernier_coup[0] + SIGNES[SIGNES.index(dernier_coup[1]) - 1])

        # retire les decalages de plus de 3 et moins que -3
        for mouvement in decal:
            i = int(mouvement[0]) - 1
            if (mouvement[1] == '+' and decalage[i] + 1 > TAILLE - 1) or (
                    mouvement[1] == '-' and decalage[i] - 1 < -TAILLE + 1):
                decal.remove(mouvement)

    return mouvements + decal


def coup(plateau, decalage, joueur, dernier_coup):
    """
    Demande un coup au joueur jusqu'à ce qu'il soit valide et le joue en modifiant le plateau
    :param plateau: liste de liste, 0 pour vide, 1 ou 2 pour joueur ou AI
    :param decalage: list d'entiers, représentent le décalage des lignes du plateau
    :param joueur: entier, 1 ou 2
    :param dernier_coup: string de deux caractères, dernier coup joué
    :return: coup joué lors du tour
    """
    # demande au joueur d'entrer son coup, vérifie que le coup est correct, et l'effectue
    fini = False
    coup_joueur = ''
    while not fini:
        coup_joueur = input('joueur ' + str(joueur) + ' > ')

        if len(coup_joueur) == 2:

            # mouvement flip
            if coup_joueur[0] in COLONNES and coup_joueur[1] in LIGNES:
                if coup_joueur == dernier_coup:
                    print("ce coup vient d'être joué")
                else:
                    i = int(coup_joueur[1]) - 1
                    j = COLONNES.index(coup_joueur[0])
                    if plateau[i][j] != joueur:
                        fini = True
                    else:
                        print('cette case est déjà de votre couleur')

            # mouvement décalage
            elif coup_joueur[0] in LIGNES and coup_joueur[1] in SIGNES:

                # mouvement inverse
                if dernier_coup is not None and coup_joueur[0] == dernier_coup[0] and coup_joueur[1] != dernier_coup[1]:
                    print("vous ne pouvez pas annuler le dernier coup joué")
                else:
                    i = int(coup_joueur[0]) - 1
                    if (coup_joueur[1] == '+' and decalage[i] + 1 < TAILLE) or \
                            (coup_joueur[1] == '-' and decalage[i] - 1 > -TAILLE):
                        fini = True
                    else:
                        print("vous ne pouvez pas décaler au-dela de trois cases à gauche et à droite")
            else:
                print('commande invalide')

        else:
            print('commande invalide')

    return coup_joueur


def minimax(plateau, decalage, dernier_coup, profondeur=2, maxi=True):
    """
    Calcule le meilleur coup pour l'AI en minimisant le score de l'adversaire et maximisant son score
    :param plateau: liste de liste, 0 pour vide, 1 pour humain, 2 pour AI
    :param decalage: list d'entiers, représentent le décalage des lignes du plateau
    :param dernier_coup: str, représentent le dernier coup joué
    :param profondeur: int, nombre de coups que l'on veut analyser
    :param maxi: bool, représente si on joue l'Ai pour Maximiser ou l'humain pour minimiser
    :return: un tuple composé d'un des meilleurs coup et du score de ce coup
    """
    gagnant = fin(plateau, decalage)

    if profondeur == 0 or gagnant:

        # scénario avec un gagnant
        if gagnant:
            if len(gagnant) == 1:
                return (None, WIN) if gagnant.pop() == JOUEUR_AI else (None, LOSS)
            else:
                return (None, DRAW)

        else:
            return (None, DRAW)

    # AI maximise le score
    elif maxi:
        meilleur_score = -10000
        meilleurs_mouvements = []
        joueur = JOUEUR_AI

    else:
        meilleur_score = 10000
        meilleurs_mouvements = []
        joueur = JOUEUR_HUMAN

    moves = mouvements_valides(plateau, decalage, dernier_coup, joueur)
    for move in moves:
        temp_plateau = deepcopy(plateau)
        temp_decalage = decalage.copy()
        coup_AI(temp_plateau, temp_decalage, joueur, move)

        # regarde le prochain coup joué par l'autre joueur
        score = minimax(temp_plateau, temp_decalage, move, profondeur - 1, not maxi)[1]

        if maxi:
            if score > meilleur_score:
                meilleur_score = score
                meilleurs_mouvements = [(move, score)]
        else:
            if score < meilleur_score:
                meilleur_score = score
                meilleurs_mouvements = [(move, score)]

        if score == meilleur_score:
            meilleurs_mouvements.append((move, score))

    return random.choice(meilleurs_mouvements)


def coup_AI(plateau, decalage, joueur, coup):
    """
    Modifie le plateau selon le coup donné
    :param plateau: liste de liste, 0 pour vide, 1 pour humain, 2 pour AI
    :param decalage: list d'entiers, représentent le décalage des lignes du plateau
    :param joueur: int, 1 pour humain, 2 pour AI
    :param coup: str, coup à jouer
    :return: None
    """

    if coup[0] in COLONNES:
        i = int(coup[1]) - 1
        j = COLONNES.index(coup[0])
        plateau[i][j] = joueur

    # mouvement décalage
    else:
        i = int(coup[0]) - 1
        if coup[1] == '+':
            decalage[i] += 1

        else:
            decalage[i] -= 1


def extract_full(dico):
    """
    Donne les Sets pour déterminer le gagnant, en filtrant les colonnes ou diagonales avec suffisamment d'éléments
    :param dico: dictionnaire avec comme clé les colonnes et comme valeur la liste des élements de la colonne ou diag
    :return: une liste de set pour chaque valeur avec une taille de 4
    """
    return [set(value) for key, value in dico.items() if len(value) == TAILLE]


def extract_diagonales(plateau, decalage):
    """
    Extrait les diagonales à partir de la première ligne
    :param plateau: liste de liste, 0 pour vide, 1 pour humain, 2 pour AI
    :param decalage: list d'entiers, représentent le décalage des lignes du plateau
    :return: deux dictionaires avec pour clé les colonnes de la première ligne et comme valeur les diagonales partant
    de ces points, de la gauche vers la droite et de la droite vers la gauche
    """
    min_indice = decalage[0]
    max_indice = TAILLE - 1 + decalage[0]
    diagonales_gd = {i: [] for i in range(min_indice, max_indice + 1)}
    diagonales_dg = {i: [] for i in range(min_indice, max_indice + 1)}

    # diagonales de la gauche vers la droite
    for col in range(min_indice, max_indice + 1):
        for i in range(TAILLE):
            for j in range(TAILLE):
                # est-ce bien sur la diagonale qu'on regarde pour le moment
                if j + decalage[i] == col + i:
                    diagonales_gd[col].append(plateau[i][j])
                if j + decalage[i] == col - i:
                    diagonales_dg[col].append(plateau[i][j])

    return diagonales_gd, diagonales_dg


def fin(plateau, decalage):
    """
        Détermine si quelqu'un a gagné
        :param plateau: liste de liste, 0 pour vide, 1 ou 2 pour joueur
        :param decalage: list d'entiers, représentent le décalage des lignes du plateau
        :return: liste vide si pas de gagnant, sinon une liste avec le ou les numéros gagnants
    """

    liste_all = []
    gagnants = []

    # colonnes et diagonales dépendent de la position de la première ligne
    min_indice = decalage[0]
    max_indice = TAILLE - 1 + decalage[0]
    colonnes = {i: [] for i in range(min_indice, max_indice + 1)}
    diagonales_gd, diagonales_dg = extract_diagonales(plateau, decalage)

    # lignes et colonnes
    for i in range(TAILLE):
        liste_all.append(set(plateau[i]))
        for j in range(TAILLE):
            if j + decalage[i] in colonnes:
                colonnes[j + decalage[i]].append(plateau[i][j])

    liste_all.extend(extract_full(colonnes))
    liste_all.extend(extract_full(diagonales_gd))
    liste_all.extend(extract_full(diagonales_dg))

    for s in liste_all:
        if len(s) == 1 and s != {0}:
            gagnants.append(s.pop())
    return gagnants


def boucle_jeu():
    """
        Lance une partie entre joueur et AI et les laisse chacun jouer un coup jusqu'à ce qu'il y ait au moins
         un gagnant
        :return: None
    """

    plateau, decalage = nouveau_plateau()
    joueur = JOUEUR_HUMAN
    gagnant = []
    dernier_coup = None

    while not gagnant:

        afficher(plateau, decalage)
        if joueur == JOUEUR_HUMAN:
            dernier_coup = coup(plateau, decalage, joueur, dernier_coup)
        # AI
        else:
            dernier_coup = minimax(plateau, decalage, dernier_coup, 2, True)[0]

        coup_AI(plateau, decalage, joueur, dernier_coup)
        gagnant = fin(plateau, decalage)
        joueur = (joueur % 2) + 1

    afficher(plateau, decalage)
    if len(set(gagnant)) == 1:
        print('joueur', gagnant.pop(), 'gagnant')
    else:
        print("Egalité !")


if __name__ == "__main__":
    boucle_jeu()