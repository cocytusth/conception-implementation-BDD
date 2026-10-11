#########################################################################
###### Noms Prenoms: Kamdem Deudjui Marc-aurel ... Nadira Aura 
###### Fatimatou Diagne ... Glaineta Mbang 
#########################################################################
#########################################################################
###### MODULE de gestion de bdd: creer/fermer connexion,
###### Creer la bdd et tables, inserer les donnees, explorer les donnees
#########################################################################
import mysql.connector as mysqlcon
import pandas as pd
    
    
def ouvrir_connexion(nom_host, nom_user, mdp_user, nom_bdd=""):
    """
    Cree une connexion au serveur MySQL.

    Args:
        nom_host (str): Le nom de l'hÃ´te oÃ¹ le serveur MySQL est situe.
        nom_user (str): Le nom de l'utilisateur pour se connecter au serveur.
        mdp_user (str): Le mot de passe de l'utilisateur pour se connecter au serveur.
        nom_bdd (str): Le nom de la base de donnees Ã  utiliser (optionnel).

    Returns:
        MySQLConnection: Une instance de connexion au serveur MySQL.
    Raises:
        mysql.connector.Error: Une erreur survient de la part de MySQL pour
                              des raisons qui peuvent inclure des problÃ¨mes
                              de connexion reseau ou des pbs lies Ã  la BDD.

    """
    connexion = None

    try:
        if nom_bdd == "" :
            connexion = mysqlcon.connect(
                host = nom_host, 
                user = nom_user, 
                password = mdp_user)
        else :
            connexion = mysqlcon.connect(
                host = nom_host, 
                user = nom_user, 
                password = mdp_user, 
                database = nom_bdd)

    except mysqlcon.Error as e:
        print("Erreur de connexion : ",e)
    
    return connexion

def fermer_connexion(connexion):
    """
    Ferme une connexion MySQL si elle est active.

    Args :
    connexion (mysql.connector.connection.MySQLConnection or None): Connexion
    active Ã  une base de donnees MySQL. Si elle est dejÃ  fermee ou None,
    la fonction ne fait rien.

    """
    try:
        if connexion is not None and connexion.is_connected():
            connexion.close()
            print("Fermeture reussie")

    except mysqlcon.Error as e:
        print("Erreur de fermeture :", e)

def selectionner_bdd(connexion, nom_bdd):
    """
    Selectionne la base de donnees specifiee pour la connexion donnee.

    Args:
        connexion (MySQLConnection or None): Connexion
        nom_bdd (str): Nom de la base de donnees Ã  selectionner.
    Raises:
        mysql.connector.Error: Une erreur de selection de la BDR
    """
    try :
        curseur = connexion.cursor()
        curseur.execute (f"USE {nom_bdd}")
        print("Database selectionee")
    
    except mysqlcon.Error as e:
        print(f"Une erreur de selection de la BDR : {e}")

    finally:
        if curseur:
            curseur.close()


def creer_bdd(connexion, nom_bdd):
    """
    Cree une nouvelle base de donnees MySQL si elle n'existe pas dejÃ 
    et la selectionne pour Ãªtre utilisee.

    Args:
        connexion (MySQLConnection): La connexion au serveur MySQL oÃ¹ la BDD sera creee.
        nom_bdd (str): Le nom de la BDD Ã  creer et selectionner.
        Affiche un message de reussite

    Raises:
        mysql.connector.Error: Une erreur survient liee Ã  MySQL lors de la creation
        Affiche le message d'erreur
    """
    try :
        curseur = connexion.cursor()
        curseur.execute(f"CREATE DATABASE IF NOT EXISTS {nom_bdd}")
        curseur.execute(f"USE {nom_bdd}")
        print("La base de donnée a été crée et selectionnée")
    except mysqlcon.Error as e:
        print(f"Une erreur de selection de la BDR : {e}")
    finally:
        if curseur:
            curseur.close()


def bdd_existe(connexion, nom_bdd):    
    """
    Verifie si une base de donnees existe sur le serveur MySQL. 
    Utile lors de la creation de la base de donnees : cela permet dâeviter
    de la recreer si elle existe dejÃ , grÃ¢ce Ã  la verification effectuee par
    bdd_existe.

    Args :
    connexion (MySQLConnection): Connexion active Ã  un serveur MySQL.
    nom_bdd (str): Nom de la base de donnees dont on veut verifier l'existence.

    Returns : bool: True si la base de donnees existe, False sinon ou en cas d'erreur.  
    Raises:
        mysql.connector.Error: Une erreur lors de la verification de
        l'existence de la BDR
    """

    curseur = None
    try:
        curseur = connexion.cursor()
        curseur.execute("SHOW DATABASES LIKE %s", (nom_bdd,))
        for database in curseur:
            if database:
                return True
        return False
        
    except mysqlcon.Error as e:
        print(f"Erreur lors de la verification de l'existence de la base de donnees : {e}")
        return False
    finally:
        if curseur:
            curseur.close()

def tables_deja_creees(connexion, liste_tables):
    """
    Verifie si toutes les tables sont dejÃ  presentes dans la base de donnees.

    Args:
        connexion (MySQLConnection): Connexion active Ã  un serveur MySQL.
        liste_tables (list[str]): Liste des noms de tables attendues.

    Returns:
        bool: True si toutes les tables sont presentes, False sinon.
    Raises:
        mysql.connector.Error
    """
    curseur = None
    existe = False
    try:
        curseur = connexion.cursor()
        curseur.execute("SHOW TABLES")
        tables_existantes = {ligne[0] for ligne in curseur.fetchall()}
        existe =  all(table in tables_existantes for table in liste_tables)
    
    except mysqlcon.Error as e:
        print(f"Erreur lors de la verification des tables : {e}")
        
    finally:
        if curseur:
            curseur.close()
            
    return existe

def get_noms_cols_table(connexion, nom_table):
    """
    RecupÃ¨re les noms des colonnes dansune table, en excluant les colonnes
    auto-incrementees.

    Args:
        connexion (MySQLConnection): Connexion active Ã  un serveur MySQL.
        nom_table (str): Nom de la table Ã  decrire.

    Returns:
        list[str]: Liste des noms de colonnes non auto-incrementees.
    """
    cur = connexion.cursor()
    cur.execute(f"DESCRIBE {nom_table}")
    colonnes = []
    for row in cur.fetchall():
        nom_col = row[0]
        extra = row[5]
        
        if "auto_increment" not in extra:
            colonnes.append(nom_col)
    
    return colonnes

def creer_tables(connexion):
    """
    Cree les differentes tables de la BDR

    Args:
        connexion (MySQLConnection): Connexion active à un serveur MySQL.

    Returns:
        None, ne renvoie rien mais affiche un message de reussite ou d'erreur
    Raises:
        mysql.connector.Error
    """
    curseur=None
    try:
        curseur = connexion.cursor()
            
        req1 = """
             create table if not exists region (
             id_region int primary key auto_increment,
             nom_region varchar(50),
             constraint uk_region unique(nom_region) );
            """  
            
        req2 = """
             create table if not exists pays (
             code_pays varchar(50) primary key,
             nom_pays varchar(50),
             id_region int, 
             population int, 
             superficie int,
             migration int,
             pibParHab int,
             foreign key (id_region) references region(id_region) on delete cascade on update cascade);
            """  
        req3 = """
             create table if not exists athlete (
             id_athlete int primary key auto_increment,
             nom varchar(30) not null,
             prenom varchar(30), 
             sexe ENUM('Women', 'Men') 
         );
            """  
        req4 = """
             create table if not exists sport (
             id_sport int primary key auto_increment,
             sport varchar(50) not null);
            """  
            
        req5 = """
             create table if not exists discipline (
             id_discipline int primary key auto_increment,
             discipline varchar(50) not null,
             id_sport int not null,
             foreign key (id_sport) references sport (id_sport) on delete cascade on update cascade) ;
            """  
            
        req6 = """
             create table if not exists epreuve (
             id_epreuve int primary key auto_increment,
             epreuve varchar(50) not null,
             id_discipline int not null,
             foreign key (id_discipline) references discipline (id_discipline) on delete cascade on update cascade);
            """  
            
        req7 = """
             create table if not exists JO (
             id_jo int primary key auto_increment,
             saison ENUM('Winter', 'Summer'), 
             annee smallint);
            """  
            
        req8 = """
             create table if not exists ville (
             id_ville int primary key auto_increment,
             ville varchar(50));
            """ 
            
        req9 = """
             create table if not exists participation (
             id_part int primary key auto_increment,
             id_athlete int not null,
             id_jo int not null,
             id_epreuve int not null,
             medaille ENUM('Gold', 'Silver', 'Bronze'),
             id_ville int, 
             code_pays varchar(50),
             unique(id_athlete, id_jo, id_epreuve, medaille,id_ville ,code_pays ),
             constraint fk_athlete foreign key (id_athlete) references athlete(id_athlete) on delete cascade on update cascade,
             constraint fk_epreuve foreign key (id_epreuve) references epreuve(id_epreuve) on delete cascade on update cascade,
             constraint fk_pays foreign key (code_pays) references pays(code_pays) on delete cascade on update cascade,
             constraint fk_jo foreign key (id_jo) references JO(id_jo) on delete cascade on update cascade,
             constraint fk_ville foreign key (id_ville) references ville(id_ville) on delete cascade on update cascade) ;
             """
        
        for sql in (req1, req2, req3, req4, req5, req6, req7, req8, req9 ):
            curseur.execute(sql)
        print("Creation des tables reussie") 
        
    except mysqlcon.Error as erreur:
        connexion.rollback()
        print(f"Il y'a une erreur dans la creation des tables : {erreur}")
    finally:
        if curseur:
            curseur.close()

def create_dicts(df,cols):
    """
    Crée une liste de dictionnaires(un dictionnaire pour chaque ligne unique)
    à partir d'un df

    Args:
        df: dataframe du jeux de données
        cols : liste des colonnes à extraire

    Returns:
        La liste de dictionnaires representant chaque éléments distincts
    """
    results=df[cols].drop_duplicates()
    dic = results.to_dict(orient="records")
    return dic

#Fonction d'insertion générale
def insert_table(connexion, data, table, col, fk={}, fk_pour2={}):
    """
    Insere les données dans une table

    Args:
        connexion (MySQLConnection): Connexion active Ã  un serveur MySQL.
        data : liste de dictionnaire contenant les différentes lignes.
        table : Nom de la table.
        col : dictionnaire avec nom_col_dans_table:nom_dans_data 
        fk : dictionnaire avec nom_col_à_inserer_dans_table:(nom_dans_data[aussi nom_table_orig],nom_dans_table_ref)
        fk_pour2 : dictionnaire avec nom_col_à_inserer_dans_table:(nomElt1_dans_table_ref/data,nomElt2_dans_table_ref/data, nom_table_ref).

    Returns:
        None, ne renvoie rien mais affiche un message de réussite ou d'erreur
    Raises:
        mysql.connector.Error
    """
    try:
        curseur = connexion.cursor()
        
        #nom des colonnes dans l'ordre d'insertion
        nom_col=",".join(tuple(col.keys())+tuple(fk.keys())+tuple(fk_pour2.keys()))
        
        #Les paramètres de la requete
        placeholders = ",".join(["%s"]*(len(col)+len(fk)+len(fk_pour2)))
        
        #Former la requete 
        req = f"insert ignore into {table}({nom_col}) values ({placeholders})"
        
        #Néttoyer les NaN en None dans tout data
        data = [{k: (None if pd.isna(v) else v) for k, v in ligne.items()} for ligne in data]
        
        # Récupérer d'abord chaque fk1 sous format : {fk:{col_data:corres_table_ref} }
        fk_col = {}
        for id_fk, (column, col_dansref) in fk.items():
            curseur.execute(f"select {col_dansref}, {id_fk} from {column}")
            fk_col[id_fk] = {row[0]: row[1] for row in curseur.fetchall()}
        
        # Récupérer d'abord chaque fk_pour2 sous format : {fk:{(col1_data, col2_data):corres_table_ref} }
        # Pour éviter les vérification et véridier direct
        fk_col2 = {}
        for id_fk, (col1, col2, table_ref) in fk_pour2.items():
            curseur.execute(f"select {col1}, {col2}, {id_fk} from {table_ref}")
            fk_col2[id_fk] = {(row[0],row[1]):row[2] for row in curseur.fetchall()}
          
        
        #Stocker les valeurs à inserer dans une liste de tuple
        valeurs = []
        for ligne in data:
            row=[]
            #Ajouter dans la ligne les valeurs propres de la colonne
            for col_data in col.values():
                row.append(ligne[col_data])
            
            #Ajouter dans la ligne les valeurs étrangères de la colonne à partir de leur correspondant fk
            for key, (col_data, col_ref) in fk.items():
                row.append(fk_col[key].get(ligne[col_data]))
            
            #Ajouter dans la ligne les valeurs étrangères correspondant à 2 comme année et saison pour J.O
            for key, (col1,col2, tab_ref) in fk_pour2.items():
                c1, c2=ligne[col1], ligne[col2]
                row.append(fk_col2[key].get((c1,c2)))
            valeurs.append(tuple(row))
        
        #Executer
        curseur.executemany(req,valeurs)
        connexion.commit()
        print(f"Insertion {table} réussie")
     
    except mysqlcon.Error as erreur:
        connexion.rollback()
        print(f"Il y'a une erreur dans l'inserion de {table} : {erreur}")
    finally:
        if curseur:
            curseur.close()
 
 #Renvoyer le nombre de participations(pour verification avant insertion)
def nb_participation(connexion) : 
      """
      Retourne le nombre de participations inserer peut 
      aide à vérifier si toutes les colonnes sont insérées.

      Paramètre :
          connexion : objet de connexion à la base de donnees.

      Returns :
          nombre de participations
      """
      curseur = connexion.cursor(dictionary = True) 
      req = """
              SELECT count(id_part) nb_par from participation;  
          """ 
      
      curseur.execute(req)
      res = curseur.fetchall()
      
      return res[0]["nb_par"] 
 
#Insertion complete
def insertion(connexion,df_jeux):
    """
    Execute toutes les insertions

    Args:
        connexion (MySQLConnection): Connexion active Ã  un serveur MySQL.
        df_jeux : data_frame

    Returns:
        None, ne renvoie rien mais affiche un message de réussite
    """
    # Insertion pour chaque table
    region = create_dicts(df_jeux, ['region',])
    insert_table(connexion, region,'region', {'nom_region': 'region'})
    
    pays = create_dicts(df_jeux, ['code_pays', 'pays','region', 'population', 'superficie', 'migration', 'pibParHab'])
    insert_table(connexion, pays, 'pays', 
             {'code_pays':'code_pays','nom_pays':'pays','population':'population','superficie' :'superficie','migration' : 'migration', 'pibParHab':'pibParHab' }, 
             fk={'id_region':('region','nom_region')})
    
    sport = create_dicts(df_jeux, ['sport',])
    insert_table(connexion,sport,'sport',{'sport':'sport'})
    
    discipline = create_dicts(df_jeux, ['discipline', 'sport'])
    insert_table(connexion, discipline, 'discipline', {'discipline':'discipline'},
                 fk={'id_sport':('sport','sport')})
    
    epreuve= create_dicts(df_jeux, ['epreuve', 'discipline'])
    insert_table(connexion,  epreuve, 'epreuve',  {'epreuve':'epreuve'},
                 fk={'id_discipline':('discipline','discipline')})
    
    athlete = create_dicts(df_jeux, ['nom', 'prenom', 'sexe'])
    insert_table(connexion, athlete, 'athlete',{'nom': 'nom', 'prenom': 'prenom', 'sexe': 'sexe'})
    
    jo = create_dicts(df_jeux, ['saison', 'annee'])
    insert_table(connexion, jo,'JO', 
                 {'saison': 'saison', 'annee': 'annee'})
    
    ville  = create_dicts(df_jeux, ['ville',])
    insert_table(connexion, ville, 'ville',      
                 {'ville': 'ville'})
    
    particip = create_dicts(df_jeux, ['nom', 'prenom', 'sexe', 'epreuve', 'medaille', 'ville', 'code_pays', 'saison', 'annee'])
    insert_table(connexion, particip, 'participation',
        {'medaille':'medaille','code_pays':'code_pays'},
        fk={'id_epreuve':('epreuve','epreuve'),'id_ville':('ville','ville')},
        fk_pour2={'id_athlete':('nom','prenom','athlete'),'id_jo':('annee','saison','JO')})
    
    print("Insertions Terminées")

#########################################################
####### Fonctions d'exploration de la bdd à  completer
#########################################################


def top_10_pays_medailles(connexion):
    """
    Retourne le top 10 des pays ayant obtenu le plus de medailles.

    Paramètre :
        connexion : objet de connexion à la base de donnees.

    Returns :
        list[dict] : liste de dictionnaires contenant le code du pays,
        le nom et le nombre total de medailles. Par exemple:
        [
            {'code_pays': 'USA', 'nom_pays': 'United States', 'total_medailles': 5637},
            {'code_pays': 'RUS', 'nom_pays': 'Russia', 'total_medailles': 3947}
        ]
    """
    curseur = connexion.cursor(dictionary = True) # recupe les results direct en dico
    req = """
            SELECT p.code_pays, nom_pays, count(medaille) as total_medailles FROM pays AS p 
            JOIN participation AS par ON p.code_pays = par.code_pays
            GROUP BY nom_pays, code_pays ORDER BY total_medailles DESC LIMIT 10 ;  
        """ 
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def classement_top_10_pays_gold_silver_bronze(connexion):
    """
    Retourne le classement des top 10 pays selon le nombre de medailles d'or,
    d'argent et de Bronze.

    Args :
        connexion : objet de connexion à la base de donnees.

    Returns :
        list[dict] : liste de dictionnaires contenant le nom du pays,
        le nombre de medailles d'or, d'argent, de Bronze et le total. Par exemple:
        [
            {'nom_pays': 'United States', 'Gold': 2638, 'Silver': 1641,
             'Bronze': 1358, 'total_medailles': 5637}
        ]
    """
    curseur = connexion.cursor(dictionary = True)
    req = """
            SELECT p.nom_pays, 
            COUNT(case when medaille = 'Gold' then 1 end) as Gold,
            COUNT(case when medaille = 'Silver' then 1 end) as Silver,
            COUNT(case when medaille = 'Bronze' then 1 end) as Bronze,
            COUNT(medaille) as total_medailles
            FROM pays AS p JOIN participation AS par ON p.code_pays = par.code_pays
            WHERE medaille in ('Gold', 'Silver', 'Bronze') GROUP BY nom_pays, p.code_pays
            ORDER BY count(medaille) DESC LIMIT 10 ; 
        """  
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def evolution_medailles_par_annee(connexion):
    """
    Retourne l'evolution du nombre total de medailles par annee.

    Args :
        connexion : objet de connexion à la base de donnees.

    Returns :
        list[dict] : liste contenant l'annee et le nombre total de medailles.
        Par exemple:
        [
            {'annee': 1896, 'total_medailles': 143},
            {'annee': 1900, 'total_medailles': 604}
        ]
    """
    curseur = connexion.cursor(dictionary = True)

    req = """
            SELECT annee, count(medaille) as total_medailles FROM jo JOIN participation as par
            ON jo.id_jo = par.id_jo GROUP BY annee ORDER BY annee ASC ;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def top_20_disciplines_medailles(connexion):
    """
    Retourne le top 20 des disciplines ayant généré le plus de médailles.

    Args :
        connexion : objet de connexion à la base de données.

    Returns :
        list[dict] : liste contenant le sport, la discipline 
        et le total de médailles. Par exemple: 
        [
            {'nom_sport': 'Aquatics', 'nom_disc': 'Swimming', 'total_medailles': 1670},
            {'nom_sport': 'Athletics', 'nom_disc': 'Athletics', 'total_medailles': 1580}
        ]
    """
    
    
    curseur = connexion.cursor(dictionary=True)

    req = """
            SELECT sport nom_sport, discipline nom_disc, count(medaille) as total_medailles FROM participation as par JOIN 
            epreuve as e ON par.id_epreuve = e.id_epreuve JOIN discipline as d 
            ON e.id_discipline = d.id_discipline JOIN sport as s ON s.id_sport = d.id_sport
            GROUP BY sport, discipline ORDER BY total_medailles DESC LIMIT 20;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def top_20_epreuves_medailles(connexion):
    """
    Retourne le top 20 des épreuves ayant généré le plus de médailles.

    Args :
        connexion : objet de connexion à la base de données.

    Returns :
        list[dict] : liste contenant le sport, la discipline, l'épreuve
        et le total de médailles. Par exemple: 
        [
            {'nom_sport': 'Athletics', 'nom_disc': 'Athletics',
             'nom_ep': '100 metres Men', 'total_medailles': 150}
        ]
    """
    curseur = connexion.cursor(dictionary=True)

    req="""
            SELECT sport nom_sport, discipline nom_disc, epreuve nom_ep, count(medaille) as total_medailles FROM participation as par JOIN 
            epreuve as e ON par.id_epreuve = e.id_epreuve JOIN discipline as d 
            ON e.id_discipline = d.id_discipline JOIN sport as s ON s.id_sport = d.id_sport
            GROUP BY sport, discipline, epreuve ORDER BY total_medailles DESC LIMIT 20;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def sports_dominants_par_pays(connexion):
    """
    Retourne, pour chaque pays, les sports dans lesquels il a obtenu
    le plus de medailles.

    Args :
        connexion : objet de connexion Ã  la base de donnees.

    Returns :
        list[dict] : liste contenant le pays, le sport et le nombre de medailles.
       Par exemple:
        [
            {'nom_pays': 'United States', 'nom_sport': 'Athletics', 'total_medailles': 1200},
            {'nom_pays': 'France', 'nom_sport': 'Fencing', 'total_medailles': 250}
        ]
    """
    curseur = connexion.cursor(dictionary = True)

    req = """
            select nom_pays, sport nom_sport, count(medaille) total_medailles
            from pays p join participation pa on p.code_pays=pa.code_pays
            natural join epreuve natural join discipline natural join sport 
            group by nom_pays, nom_sport ;
        """
    
    curseur.execute(req)
    #Récupérer le nombre de médaille des pays pour toutes les disciblines
    res_all = curseur.fetchall()
    
    #Initier un dictionnaire qui contient les max_nbMedal et res
    max_nbMedal={}
    for elt in res_all:
        # Remplace seulement le max du pays < elt_nb_medailles
        if max_nbMedal.get(elt["nom_pays"],0) < elt["total_medailles"]:
            max_nbMedal[elt["nom_pays"]] = elt["total_medailles"]
    #Ajouter à res seulement s'il a le max_nbMedal du pays
    res=[]
    for elt in res_all:
        if max_nbMedal.get(elt["nom_pays"],0) == elt["total_medailles"]:
            res.append(elt)
                 
    return res

def medailles_region_saison(connexion):
    """
    Retourne le nombre de medailles par region et par saison
    des Jeux Olympiques.

    Args :
        connexion : objet de connexion à la base de donnees.

    Returns :
        list[dict] : liste contenant la region, la saison et le total de medailles.
        Par exemple: 
        [
            {'nom_reg': 'Europe', 'saison': 'Summer', 'total_medailles': 8500},
            {'nom_reg': 'Europe', 'saison': 'Winter', 'total_medailles': 2100}
        ]
    """
    curseur = connexion.cursor(dictionary=True)

    req="""
        SELECT nom_region AS nom_reg, saison, COUNT(medaille) AS total_medailles FROM region AS r JOIN pays AS p  
        ON p.id_region = r.id_region JOIN participation AS par ON par.code_pays = p.code_pays 
        JOIN jo ON par.id_jo = jo.id_jo GROUP BY nom_reg, saison ;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()

    return res

def total_medailles_par_sexe(connexion):
    """
    Retourne le nombre total de medailles par sexe.

    Args :
        connexion : objet de connexion à la base de donnees.

    Retour :
        list[dict] : liste contenant le sexe et le total de medailles.

    Exemple de sortie :
        [
            {'sexe': 'Men', 'total_medailles': 18000},
            {'sexe': 'Women', 'total_medailles': 9500}
        ]
    """
    curseur = connexion.cursor(dictionary=True)

    req="""
            SELECT sexe, COUNT(medaille) AS total_medailles FROM participation pa
            JOIN athlete a ON pa.id_athlete = a.id_athlete GROUP BY a.sexe
            ORDER BY total_medailles DESC ;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def top_10_sports_femmes_medailles(connexion):
    """
    Retourne le top 10 des sports où les femmes ont obtenu
    le plus de medailles.

    Args :
        connexion : objet de connexion à la base de donnees.

    Retour :
        list[dict] : liste contenant le sport et le total de medailles
        obtenues par des femmes.

    Exemple de sortie :
        [
            {'nom_sport': 'Aquatics', 'total_medailles_femmes': 1200},
            {'nom_sport': 'Athletics', 'total_medailles_femmes': 980}
        ]
    """
    curseur = connexion.cursor(dictionary=True)

    req="""
            SELECT sport nom_sport, COUNT(medaille) AS total_medailles_femmes FROM sport as s
            JOIN discipline as d ON s.id_sport = d.id_sport JOIN epreuve as e
            ON d.id_discipline = e.id_discipline JOIN participation as par
            ON e.id_epreuve = par.id_epreuve JOIN athlete as a 
            ON par.id_athlete = a.id_athlete WHERE sexe = "Women" 
            GROUP BY sport ORDER BY total_medailles_femmes DESC LIMIT 10 ;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def impact_pib_medailles(connexion):
    """
    Retourne les pays classes selon leur PIB par habitant et leur nombre
    total de medailles.

    Les categories utilisees sont :
        - Pays pauvre : PIB par habitant < 4500
        - Pays intermediaire : PIB par habitant entre 4500 et 14000
        - Pays riche : PIB par habitant > 14000
        - Non renseigne : PIB manquant

    Args :
        connexion : objet de connexion Ã  la base de donnees.

    Returns :
        list[dict] : liste contenant le pays, le PIB par habitant,
        la categorie de PIB et le total de medailles. Par exemple:

        [
            {'nom_pays': 'France', 'pibParHab': 36000,
             'categorie_pib': 'Pays riche', 'total_medailles': 950}
        ]
    """
    curseur = connexion.cursor(dictionary=True)

    req="""
            select nom_pays, pibParHab, 
            	CASE
            	WHEN pibParHab < 4500 THEN 'Pays pauvre'
            	WHEN pibParHab <= 14000 THEN 'Pays intermediaire'
            	WHEN pibParHab > 14000 THEN 'Pays riche'
            	ELSE 'Non renseigne' 
            	END AS category_pib, count(medaille) total_medailles
            from pays p join participation pa on p.code_pays=pa.code_pays
            group by nom_pays, pibParHab,category_pib
            order by pibParHab;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def impact_population_medaille(connexion):
    """
    Retourne les pays classes selon leur population et leur nombre total
    de medailles.

    Les categories utilisees sont :
        - Petit pays : population < 10 000 000
        - Pays moyen : population entre 10 000 000 et 100 000 000
        - Grand pays : population > 100 000 000
        - Non renseigne : population manquante

    Args :
        connexion : objet de connexion Ã  la base de donnees.

    Returns :
        list[dict] : liste contenant le pays, la population,
        la categorie de population et le total de medailles.
        Par exemple: 
        [
            {'nom_pays': 'China', 'population': 1400000000,
             'categorie_population': 'Grand pays', 'total_medailles': 1100}
        ]
    """
    
    curseur = connexion.cursor(dictionary=True)

    req="""
            select nom_pays, population, 
            	CASE
            	WHEN population < 10000000 THEN 'Petit pays'
            	WHEN population <= 100000000 THEN 'Pays moyen'
            	WHEN population > 100000000 THEN 'Grand pays'
            	ELSE 'Non renseigne' 
            	END AS category_population, count(medaille) total_medailles
            from pays p join participation pa on p.code_pays=pa.code_pays
            group by nom_pays,population, category_population
            order by population;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res


#Ajout

#Récuperer les kpis
def kpis_dashboard(connexion):
    """
    Calcule des indicateurs globaux (KPIs) à partir de la base.
    Retourne un dictionnaire contenant :
    - le nombre de pays, d'athlete, de participation
    - Nombre de medailles : Silver, Gold, Bronze

    Args:
    connexion : objet de connexion Ã  la base de donnees.

    Returns:
    [ {nom_kpi: valeur} ]
    """
    
    curseur = connexion.cursor(dictionary=True)

    req = """
                SELECT
                    (SELECT count(id_athlete) FROM athlete) AS Nbre_athlete,
                    (SELECT count(DISTINCT code_pays) FROM participation) AS Nbre_pays,
                    (SELECT count(DISTINCT id_part) FROM participation) AS Nbre_participation,
                    (SELECT count(DISTINCT id_part) FROM participation where medaille="Silver") AS Nbre_silver,
                    (SELECT count(DISTINCT id_part) FROM participation where medaille="Bronze") AS Nbre_Bronze,
                    (SELECT count(DISTINCT id_part) FROM participation where medaille="Gold") AS Nbre_gold;
                """
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res


#Medailles par categoriepib
def catpib_medailles(connexion):
    """
    Retourne les categories pib des pays selon leur nombre
    total de medailles.

    Les categories utilisees sont :
        - Pays pauvre : PIB par habitant < 4500
        - Pays intermediaire : PIB par habitant entre 4500 et 14000
        - Pays riche : PIB par habitant > 14000
        - Non renseigne : PIB manquant

    Args :
        connexion : objet de connexion Ã  la base de donnees.

    Returns :
        list[dict] : liste contenant
        la categorie de PIB et le total de medailles. Par exemple:

        [
            {'categorie_pib': 'Pays riche', 'total_medailles': 950}
        ]
    """
    curseur = connexion.cursor(dictionary=True)

    req="""
            select
                CASE
            	WHEN pibParHab < 4500 THEN 'Pays pauvre'
            	WHEN pibParHab <= 14000 THEN 'Pays intermediaire'
            	WHEN pibParHab > 14000 THEN 'Pays riche'
            	ELSE 'Non renseigne' 
            	END AS category_pib, count(medaille) total_medailles
            from pays p join participation pa on p.code_pays=pa.code_pays
            group by category_pib;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res

def catpop_medaille(connexion):
    """
    Retourne les pays classes selon leur population et leur nombre total
    de medailles.

    Args :
        connexion : objet de connexion Ã  la base de donnees.

    Returns :
        list[dict] :
        la categorie de population et le total de medailles.
        Par exemple: 
        [
            {'categorie_population': 'Grand pays', 'total_medailles': 1100}
        ]
    """
    
    curseur = connexion.cursor(dictionary=True)

    req="""
            select
            	CASE
            	WHEN population < 10000000 THEN 'Petit pays'
            	WHEN population <= 100000000 THEN 'Pays moyen'
            	WHEN population > 100000000 THEN 'Grand pays'
            	ELSE 'Non renseigne' 
            	END AS category_population, count(medaille) total_medailles
            from pays p join participation pa on p.code_pays=pa.code_pays
            group by category_population;
        """
    
    curseur.execute(req)
    res = curseur.fetchall()
    
    return res
# pour tester les differentes fonctions developpees
if __name__ == "__main__":
    nom_bdd = "bdd_jo"
    #tester vos fonctions
    """
        Tests effectué sur jupiter notebook
    """