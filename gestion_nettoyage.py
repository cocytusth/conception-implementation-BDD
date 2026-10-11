#########################################################################
###### Noms Prenoms: Kamdem Deudjui Marc-aurel ... Nadira Aura 
###### Fatimatou Diagne ... Glaineta Mbang 
#########################################################################

#########################################################################
###### MODULE de gestion de creation et nettoyage du dataframe
#########################################################################

import pandas as pd
import numpy as np
import string

### Fonctions utilitaires à écrire si besoin pour vous aider dans le nettoyage

#Fonction pour renvoyer le nombre de valeurs abhérentes pour une colonne
def aberrant(x,df) :
    Q1 = np.percentile(df[x], 25)
    Q3 = np.percentile(df[x], 75)
    IQR = Q3 - Q1
    return df[(df[x] < Q1 - 1.5*IQR) & (df[x] > Q3 +1.5*IQR)].shape[0]

#Fonction de néttoyage des chaines de caractère
def clean(x):
    if not isinstance(x, str) : return None
    #Espace au bord
    x = x.strip()
    if x=="" : return None #si c'est vide apres le strip on met null
    #Capitalize
    x = x.capitalize()
    #Initialiser la nouvelle chaine
    res=""
    dernier_res = ""
    
    #Parcourir la chaine
    for i in x:
        #Ajouter si pas un espaces supplementaire et caractère valide
        if i.isalnum() or i in "/ -," : 
            if not(dernier_res==" " and i==" "):
                res = res + i
                dernier_res = i
    return res

def nettoyer_preparer_donnees(nom_fichier):
    """
    Cette fonction charge un fichier CSV, effectue un nettoyage de données complet,
    et prépare les données pour une analyse ultérieure.

    Étapes de traitement :
    1. Conversion des types de données où nécessaire
    2. Gestion des données manquantes
    3. Détection et suppression des duplications dans le DataFrame.
    4. Normalisation des données pour corriger les incohérences et les fautes de frappe
    5. Vérification et traitement des valeurs aberrantes.
    
    Args :
    - nom_fichier (str): Le chemin vers le fichier CSV à charger.

    Returns :
    - pd.DataFrame : Le DataFrame nettoyé et préparé.
    Raises:
        En cas d’erreur, un message est affiché mais l'exception n’est pas propagée.

    """
    df_jeux = None
    try:
        
        # Création du data frame
        df_jeux = pd.read_csv(nom_fichier)
        print("Les données sont chargées avec succés")
        
        # Vérification de la structure 
        """df_jeux.head(n=5)"""
        
        
        ###########################
        #étape 1: Type de donnees et format 
        ###########################
        
        """ 
            #Vérification du type des colonnes
            df_jeux.dtypes
        """
        
        # Remplacer les virgules avec les points dans densité et migration
        df_jeux["densite"] = df_jeux["densite"].str.replace(",", ".")
        df_jeux["migration"] = df_jeux["migration"].str.replace(",", ".")
        
        # changer les types
        df_jeux["population"] = pd.to_numeric(df_jeux["population"], errors="coerce")
        df_jeux["migration"] = pd.to_numeric(df_jeux["migration"], errors="coerce")
        df_jeux["densite"] = pd.to_numeric(df_jeux["densite"], errors="coerce")
        
        # Format de pibParHab 
        df_jeux["pibParHab"] = round(df_jeux["pibParHab"],2)

        """ 
            #Vérification des nouveaux types et formats des colonnes
            df_jeux.dtypes
        """
        

        ##############################
        #étape 2: Données manquantes #
        ##############################
        
        """ 
            #Valeurs manquantes par colonnes
            print(df_jeux.isnull().sum())
        """
        
        #Supprimer les lignes sans pays
        df_jeux = df_jeux.dropna(subset = ["pays"])
        
        #Remplacer par inconnues les na de région
        df_jeux["region"] = df_jeux["region"].fillna("Inconnue")
        
        """ 
            # Verification Valeurs manquantes par colonnes
            print(df_jeux.isnull().sum())
        """


        ##############################
        #étape 3: Trouver les duplications
        ###############################
        
        """ #Nombres de lignes dupliqué
            df_jeux.duplicated().sum()
            #Localisation de ces lignes
        """
        
        #Suppression des doublons
        df_jeux = df_jeux.drop_duplicates()
        
        """ #Vérification
            df_jeux.duplicated().sum()
            df_jeux.loc[df_jeux.duplicated()]
        """


        ##############################
        #étape 4: Incohérences et Types
        ###############################
        
        #Colonnes concernées
        colonnes_str = df_jeux.select_dtypes(include = ["object"]).columns
        print(colonnes_str)
        
        #Appliquer  la normalisation grace à la fonction clean
        for x in colonnes_str :
            df_jeux[x] = df_jeux[x].apply(clean)
            
        #Remettre en lettre capitales de code pays,région
        df_jeux["code_pays"] = df_jeux["code_pays"].str.upper()
        df_jeux["region"] = df_jeux["region"].str.upper()
        
        """#Vérification
            df_jeux
        """
        

        ##############################
        #étape 5: les valeurs aberrantes
        ###############################
        
        #Valeurs nulle par élement
        val_ab = {}
        for x in ["annee", "densite","population","migration","pibParHab", "superficie"]:
            val_ab[x] = aberrant(x,df_jeux)
            
        """print(val_ab)"""
        
        """On a aucune valeurs abérantes pour toutes les colonnes"""
         
        
        ##############################
        #étape 6: Nouvelles colonnes
        ###############################
        
        #Séparer en 2 éléments le nom et prenom
        athlete = df_jeux["athlete"].str.split(",",expand = True)
        
        #Nouvelles colonnes
        df_jeux["nom"] = athlete[0]
        df_jeux["prenom"] = athlete[1] + athlete[2].apply(lambda x : x if x is not None else "")
        
        #Suppression de l'ancienne colonne
        df_jeux = df_jeux.drop("athlete", axis="columns")
        
        #Réordonner
        reorder = ["annee", "ville", "sport", "discipline", "nom", "prenom", "code_pays","sexe", 
                   "epreuve", "medaille", "saison", "pays", "population", "region", 
                   "superficie", "densite", "migration", "pibParHab"]
        
        df_jeux = df_jeux.reindex(columns=reorder)
        
        """ 
            # Verification Valeurs manquantes par colonnes
               print(df_jeux.isnull().sum())
            # Verification Ligne nulle
                prenom_null = df_jeux["prenom"].isnull()
                df_jeux[prenom_null]
        """
        
        #Normalisation des nouvelles colonnes
        df_jeux["prenom"] = df_jeux["prenom"].apply(clean)
        df_jeux["nom"] = df_jeux["nom"].apply(clean).str.upper()
        
        """
            # Verification nouvelle structure
                df_jeux
        """

    except FileNotFoundError as ffe:
        print(f"Erreur!!Fichier non existant ({ffe})")
    except Exception as e:
        print("Erreur inconnue :", e)
        
    return df_jeux

if __name__ == "__main__":
    nom_fichier = "jeux_olympiques.csv"
    #Tester si le nettoyage est bon
    df_jeux = nettoyer_preparer_donnees(nom_fichier)