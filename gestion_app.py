#########################################################################
###### Noms Prenoms: Kamdem Deudjui Marc-aurel ... Nadira Aura 
###### Fatimatou Diagne ... Glaineta Mbang 
#########################################################################

#########################################################################
###### MODULE de gestion de l'application
#########################################################################
#importer les deux modules de gestionnaire de bdd et nettoyage
import gestion_bdd as gbd
import gestion_nettoyage as clean

#Fonction de reporting
from openpyxl import Workbook, load_workbook
from openpyxl.chart import PieChart, BarChart, LineChart, Reference
import os


def inserer_feuille_et_graph_openpyxl(res, nom_fichier, nom_feuille, titre="", type_diag="bar", titre_x=None,titre_y=None, avec_graphique=False):
    """
    Insère une feuille dans un fichier Excel avec un graphique (pie ou bar).

    Args:
        res (list[dict]): Résultat d'une requête SQL sous forme de liste de dictionnaires
        nom_fichier (str): Nom du fichier Excel (ex : "stats_jo.xlsx")
        nom_feuille (str): Nom de la feuille à insérer
        titre (str): Titre du graphique
        titre_x (str): Titre de l'axe X du graphique s'il existe
        titre_y (str): Titre de l'axe Y du graphique s'il existe
        type_diag (str): Type de graphique (pie, line ou bar)
        avec_graphique (bool): permet de créer une feuille sans graphique
    Returns:
        None
    """
    if not res:
        print("Données vides : rien à insérer.")
        return

    # Déduire dynamiquement les clés (colonnes)
    colonnes = list(res[0].keys())

    # Charger ou créer le classeur Excel
    if os.path.exists(nom_fichier):
        wb = load_workbook(nom_fichier)
    else:
        wb = Workbook()

    #Supprimer la feuille par défaut si elle existe
    if "Sheet" in wb.sheetnames:
        std = wb["Sheet"]
        wb.remove(std)
    # Supprimer la feuille si elle existe déjà
    if nom_feuille in wb.sheetnames:
        del wb[nom_feuille]

    # Créer une nouvelle feuille
    ws = wb.create_sheet(title=nom_feuille)

    # Ajouter l'en-tête
    ws.append([col for col in colonnes])

    # Ajouter les lignes de données
    for ligne in res:
        ws.append([ligne[col] for col in colonnes])

    #Si on veut juste sauvegarder les données sans créer de graphique
    if not avec_graphique:
        wb.save(nom_fichier)
        print(f"Insertion de la feuille {nom_feuille} réussie")
        return
        
    # Définir les références pour le graphique
    n = len(res)
    data_ref = Reference(ws, min_col=len(colonnes), min_row=1, max_row=n + 1)
    labels_ref = Reference(ws, min_col=1, min_row=2, max_row=n + 1)
    
    type_diag = type_diag.lower()
    # Créer le graphique
    if type_diag == "pie":
        diag = PieChart()
        diag.title = f"{titre}"
        diag.add_data(data_ref, titles_from_data=True)
        diag.set_categories(labels_ref)
        diag.varyColors = True
        
    elif type_diag == "bar":
        diag = BarChart()
        diag.title = f" {titre}"
        diag.y_axis.title = titre_y
        diag.x_axis.title = titre_x
        diag.add_data(data_ref, titles_from_data=True)
        diag.set_categories(labels_ref)
        diag.varyColors = True
        
    elif type_diag == "line":
        diag = LineChart()
        diag.title = titre
        diag.y_axis.title = titre_y
        diag.x_axis.title = titre_x
        diag.add_data(data_ref, titles_from_data=True)
        diag.set_categories(labels_ref)

        # Style Excel coloré pour la courbe
        diag.style = 13

    else:
        print("Type de graphique invalide (choisir 'pie', 'bar' ou 'line').")
        return

    # Ajouter le graphique dans la feuille
    ws.add_chart(diag, "E2")

    # Sauvegarder
    wb.save(nom_fichier)
    print(f"Insertion de la feuille {nom_feuille} réussie")


def orchestrer_app(nom_fichier, nom_bdd):
    """
    Cette fonction orchestre le fonctionnement de votre application. 
    Voici les étapes à faire:
    1- Créer une seule instance de connexion
    2- Vérifier si la bdd et les tables existent, si oui allez à l'étape 4 relative à l'exploration 
       des données. 
       Sinon, 
            a- Créer la bdd et les différentes tables
            b- Appliquer le nettoyage sur le jeu de données et récupérer 
            un jeu nettoyé
            c- Insérer les données dans les tables
    4- Explorer les données à partir de la bdd, générer les stats et sauvegarder
    dans un fichier Excel ( Insérer trois diagrammes uniquement)
    5- Fermer la connexion
    
    Args:
    nom_fichier (str): le nom du fichier à lire
    nom_bdd (str): le nom de la BDD à explorer 
    
    Returns:
        None 
    """ 
    #Creer connexion
    connexion = gbd.ouvrir_connexion(nom_host="localhost", nom_user="root", mdp_user="toulouse")
    
    #Vérifier l'existence de la bdd
    if not gbd.bdd_existe(connexion, nom_bdd):
        #Creer la bdd si elle n'existe pas et la selectionner
        gbd.creer_bdd(connexion, nom_bdd)
    else:
        #selectionner la bdd
        gbd.selectionner_bdd(connexion, nom_bdd)
    
    #Vérifier l'existence des tables
    liste_tables=["region","athlete","participation","ville","JO","epreuve","pays","discipline","sport"]
    if not gbd.tables_deja_creees(connexion, liste_tables):
        gbd.creer_tables(connexion)
    
    #Nettoyer le jeu de donnée pour l'insertion
    df_jeux = clean.nettoyer_preparer_donnees(nom_fichier)
        
    #Insertion pour chaque tables si vides
    if gbd.nb_participation(connexion)==0:
        gbd.insertion(connexion, df_jeux)
    else : print("Jeux de données déja insérés")
    
    #Exploration et reporting
    res1 = gbd.top_10_pays_medailles(connexion)
    inserer_feuille_et_graph_openpyxl(res1,'statistiques_jo.xlsx', 
                                      'top10Pays_medal', 
                                      titre="top 10 des pays médaillés",
                                      titre_x="Pays", titre_y='Nombre de medailles',avec_graphique=True)
    
    res2 = gbd.classement_top_10_pays_gold_silver_bronze(connexion)
    inserer_feuille_et_graph_openpyxl(res2, 'statistiques_jo.xlsx', 'top10Pays_typemedal')
    
    
    res3 = gbd.evolution_medailles_par_annee(connexion)
    inserer_feuille_et_graph_openpyxl(res3, 'statistiques_jo.xlsx', 
                                      'trend_medalPerYear',titre= "Evolution du nombre de medailles par années",
                                      titre_x="Année", titre_y='Nombre de medailles', type_diag='line',
                                      avec_graphique=True)
   
    res4 = gbd.top_20_disciplines_medailles(connexion)
    inserer_feuille_et_graph_openpyxl(res4, 'statistiques_jo.xlsx','top20disc_medal')
   
    res5 = gbd.top_20_epreuves_medailles(connexion)
    inserer_feuille_et_graph_openpyxl(res5, 'statistiques_jo.xlsx','top20ep_medal')
    
    res5 = gbd.sports_dominants_par_pays(connexion)
    inserer_feuille_et_graph_openpyxl(res5, 'statistiques_jo.xlsx', 'bestSport_pays')
    
    res6 = gbd.medailles_region_saison(connexion)
    inserer_feuille_et_graph_openpyxl(res6, 'statistiques_jo.xlsx', 'medal_reg_Saison')
    
    res7=gbd.total_medailles_par_sexe(connexion)
    inserer_feuille_et_graph_openpyxl(res7,  'statistiques_jo.xlsx', 
                                      'medal_sexe', titre="Répartition des médailles par sexe",
                                      type_diag="pie",avec_graphique=True)
    
    res8 = gbd.top_10_sports_femmes_medailles(connexion)
    inserer_feuille_et_graph_openpyxl(res8, 'statistiques_jo.xlsx','Top10_medalwomenPerSport')
    
    res9 = gbd.impact_pib_medailles(connexion)
    inserer_feuille_et_graph_openpyxl(res9, 'statistiques_jo.xlsx','impact_pibParPays')
    
    res10 = gbd.impact_population_medaille(connexion)
    inserer_feuille_et_graph_openpyxl(res10, 'statistiques_jo.xlsx','impact_popParPays')
    
    res11 = gbd.kpis_dashboard(connexion)
    inserer_feuille_et_graph_openpyxl(res11, 'statistiques_jo.xlsx', 'KPI')
    
    res12 = gbd.catpib_medailles(connexion)
    inserer_feuille_et_graph_openpyxl(res12, 'statistiques_jo.xlsx', 'impact_pib')
    
    res13 = gbd.catpop_medaille(connexion)
    inserer_feuille_et_graph_openpyxl(res13, 'statistiques_jo.xlsx', 'impact_pop')
    
    #Fermer la connexion
    gbd.fermer_connexion(connexion)
    
if __name__ == "__main__":
    nom_fichier = "data/jeux_olympiques.csv"
    nom_bdd = "bdd_jo"
    
    #appel de la fonction 
    orchestrer_app(nom_fichier, nom_bdd)
    #Partie exploration et reporting
    
    