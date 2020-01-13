import pymongo


class MongoDBWorker:
    """
    Wrapper over mongo database
    """

    def __init__(self, database, host="localhost", port=27017):
        """
        :param database: name of the database which will be used
        :param host: host on which mongo db is
        :param port: port to which connect with mongo db
        """
        self.client = pymongo.MongoClient(host, port)
        self.database = self.client[database]

    def insert(self, collection, document):
        """
        :param collection: collection in which insert
        :param document: document which have to be inserted

        Insert document in collection.
        """
        return self.database[collection].insert(document)

    def get(self, collection, field=None, value=None, filter=None):
        """
        :param collection: collection in which find
        :param field: field which have to be checked
        :param value: field must be equal this value
        :param filter: selection filter. Used when search fields more than one.

        Return found documents in collection.
        """
        if field:
            return self.database[collection].find({field: value})
        elif filter:
            return self.database[collection].find(filter)
        else:
            return self.database[collection].find()

    def update(self, collection, field, value, data_for_update, upsert=False):
        """
        :param collection: collection in which find
        :param field: field which have to be checked
        :param value: field must be equal this value
        :param data_for_update: data for update
        :param upsert: if True, value will be insert in database if don`t exist documents with selection criteria

        Update documents in collection.
        """
        self.database[collection].update({field: value}, {"$set": data_for_update}, upsert=upsert)

    def replace(self, collection, field, value, replacement):
        """
        :param collection: collection in which replace
        :param field: field which have to be checked
        :param value: field must be equal this value
        :param replacement: document by which replace

        Replace documents in collection.
        """
        self.database[collection].replace_one({field: value}, replacement)

    def delete(self, collection, field, value):
        """
        :param collection: collection in which delete
        :param field: field which have to be checked
        :param value: field must be equal this value

        Delete documents in collection.
        """
        self.database[collection].delete_one({field: value})
