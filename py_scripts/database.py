import os
import os.path as osp
import sqlite3 as sql3



class DB(object):
    def __init__(self):
        self.db_filename = "sanctions_list_database.db"
        self.db_folder = "database"
        self.db_path = osp.join(self.db_folder, self.db_filename)
        
    def generate_DB(self):
      if not osp.isfile(self.db_path):
        try:
              with sql3.connect(self.db_path) as con:
                cur = con.cursor()
                cur.execute("""CREATE TABLE Individual ( 
                              individual_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                              name        TEXT,
                              gender      TEXT,
                              nationality TEXT,
                              reason      TEXT,
                              FOREIGN KEY (reason) REFERENCES Categorization(reason)
                              );""")
                con.commit()
                
                cur.execute("""CREATE TABLE Document ( 
                              document_id  INTEGER PRIMARY KEY AUTOINCREMENT, 
                              title        TEXT
                              );""")
                con.commit()
                                
                cur.execute("""CREATE TABLE Actor ( 
                              actor_id     INTEGER PRIMARY KEY AUTOINCREMENT, 
                              code         TEXT
                              );""")
                
                cur.execute("""CREATE TABLE Category ( 
                              label        TEXT PRIMARY KEY, 
                              description  TEXT
                              );""")
                
                cur.execute("""CREATE TABLE Categorization (
                                reason TEXT PRIMARY KEY,
                                label  TEXT,
                                FOREIGN KEY (label) REFERENCES Category(label)
                            );""")

                cur.execute("""CREATE TABLE Sanction ( 
                              document_id INTEGER,
                              individual_id INTEGER,
                              start_date TEXT,
                              FOREIGN KEY (document_id) REFERENCES Document(document_id),
                              FOREIGN KEY (individual_id) REFERENCES Individual(individual_id)
                              
                              );""")
                
                cur.execute("""CREATE TABLE Subscription ( 
                              document_id INTEGER,
                              actor_id    INTEGER, 
                              FOREIGN KEY (document_id) REFERENCES Document(document_id),
                              FOREIGN KEY (actor_id) REFERENCES Actor(actor_id)
                              );""")
                con.commit()
              print("\n-You made it!")  
        except sql3.Error as e:
           warning_msg = "\nERROR: Database creation failed: " + str(e)
           print(warning_msg)
      else:
          print("\nALERT: database già presente!")   
          pass 
      

db = DB()

db.generate_DB()
