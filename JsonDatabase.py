import json
import os

class JsonDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self.data = self._load_data()

    def _load_data(self):
        """
        Charge les données depuis le fichier JSON, si le fichier existe.
        :return: Dictionnaire des données de la base de données.
        """
        if os.path.exists(self.db_file):
            with open(self.db_file, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}  # Retourne un dictionnaire vide si le fichier est corrompu
        return {}

    def _save_data(self):
        """
        Sauvegarde les données dans le fichier JSON.
        """
        with open(self.db_file, "w") as file:
            json.dump(self.data, file, indent=4)

    def add_record(self, record_id, record_data):
        """
        Ajoute un enregistrement avec un identifiant unique.
        :param record_id: L'ID unique pour l'enregistrement.
        :param record_data: Les données à ajouter pour l'enregistrement.
        """
        if record_id in self.data:
            print(f"Un enregistrement avec l'ID '{record_id}' existe déjà.")
            return
        self.data[record_id] = record_data
        self._save_data()
        print(f"Enregistrement ajouté avec succès : {record_id}")

    def update_record(self, record_id, updated_data):
        """
        Met à jour un enregistrement existant.
        :param record_id: L'ID de l'enregistrement à mettre à jour.
        :param updated_data: Les nouvelles données.
        """
        if record_id not in self.data:
            print(f"Aucun enregistrement trouvé avec l'ID '{record_id}'.")
            return
        self.data[record_id].update(updated_data)
        self._save_data()
        print(f"Enregistrement '{record_id}' mis à jour avec succès.")

    def delete_record(self, record_id):
        """
        Supprime un enregistrement de la base de données.
        :param record_id: L'ID de l'enregistrement à supprimer.
        """
        if record_id not in self.data:
            print(f"Aucun enregistrement trouvé avec l'ID '{record_id}'.")
            return
        del self.data[record_id]
        self._save_data()
        print(f"Enregistrement '{record_id}' supprimé avec succès.")

    def get_record(self, record_id):
        """
        Récupère un enregistrement de la base de données.
        :param record_id: L'ID de l'enregistrement à récupérer.
        :return: Les données de l'enregistrement ou None si non trouvé.
        """
        return self.data.get(record_id, None)