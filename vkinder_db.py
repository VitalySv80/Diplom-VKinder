import sqlalchemy
import config


class Vkinderdb:
    user_name = config.vkinder_db_user
    user_pass = config.vkinder_db_pass
    db_host = config.vkinder_db_host
    db_port = config.vkinder_db_port
    db_name = config.vkinder_db_name

    def __init__(self):
        db = f'postgresql://{self.user_name}:{self.user_pass}@{self.db_host}:{self.db_port}/{self.db_name}'
        engine = sqlalchemy.create_engine(db)
        self.connection = engine.connect()
        connect_table = self.create_table()

    def create_table(self):
        connect_table = self.connection.execute("""create table if not exists Vkinder_Candidate 
                                                (
                                                ID serial primary key,
                                                VkUserID integer not null,
                                                VkCandidateID integer not null
                                                );
                                                """)
        return connect_table

    def insert_user(self, userid, candidateid):
        connect_table = self.connection.execute(f"""INSERT INTO Vkinder_Candidate(VkUserID, VkCandidateID)
                                                VALUES ({userid},{candidateid})
                                                """)

    def get_users(self, userid):
        """Возвращает массив с ID пользователей, которые уже показывались пользователю"""
        connect_table = self.connection.execute(f"""SELECT VkCandidateID from Vkinder_Candidate
                                                WHERE VkUserID = {userid}
                                                """).fetchall()
        candidate_list = []
        for el in connect_table:
            candidate_list.append(el[0])
        return candidate_list

    def clear_table(self):
        connect_table = self.connection.execute("""DROP TABLE IF EXISTS Vkinder_Candidate""")
        connect_table = self.create_table()
        return connect_table
