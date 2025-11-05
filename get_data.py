
from dotenv import load_dotenv
import os
import pymongo
import certifi

load_dotenv()

def timestamp_to_millis(timestamp_str):
    hh, mm, ss, mmm = map(int, timestamp_str.split(':'))
    return (hh * 3600 + mm * 60 + ss) * 1000 + mmm

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self,user_name="SenseORAN",password="SenseORANFeb21",cluster="orancluster.5njsvyr"):
        if hasattr(self, 'uri'):  # Check if instance already initialized
            return
        
        self.uri = "mongodb://localhost:27017"
        self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=5000)

        self.current_timestamp = 0

        self.load_csv()
        self.load_log_file()

        self.scheduling_policy_map = {
            0:"Round Robin",
            1:"Water Filling",
            2:"Proportionally Fair"
        }
    

    def load_log_file(self, db_name='log_file'):
        """
        Read the 'log' collection from the 'myDatabase' database and build self.log_data.
        This avoids relying on self.db existing and is defensive about missing documents.
        """
        try:
            # database.py inserted the log document into database "myDatabase", collection "log"
            collection = self.client['myDatabase']['log']
        except Exception:
            # fallback: try to use any existing self.db if present
            try:
                collection = getattr(self, 'db', None)
                if collection is None:
                    self.log_data = {}
                    return
            except Exception:
                self.log_data = {}
                return

        # Prefer to find the document with _id == "log_file" (this is how database.py stored it)
        row = collection.find_one({"_id": "log_file"})
        if not row:
            # If that document does not exist, try to get the first document in the collection
            row = collection.find_one()

        if not row or 'entries' not in row:
            self.log_data = {}
            return

        # Now build sorted data and the mapping
        try:
            data = sorted(row['entries'], key=lambda x: x.get('unix_epoch', 0))
        except Exception:
            # If sorting fails, fallback to the list as-is
            data = row.get('entries', [])

        self.log_data = {}
        for record in data:
            try:
                # readable_timestamp is like "YYYY-MM-DD HH:MM:SS:MMM" — we use the time part
                time_part = record.get('readable_timestamp', '').split(' ')[1]
                timestamp = timestamp_to_millis(time_part)
                self.log_data[timestamp] = record.get('class')
            except Exception:
                # skip malformed entries
                continue
            

    def load_other_csv_columns(self, db_collection, column_name):
        """
        Read single-column documents stored in the 'csv' collection inside the 'myDatabase' DB.
        db_collection can be ignored (kept for compatibility); we will explicitly open the collection.
        Returns a dict mapping timestamp_ms -> value.
        """
        output_dic = {}

        # The original populater used database 'myDatabase' and collection 'csv'
        # so explicitly point there:
        try:
            collection = self.client['myDatabase']['csv']
        except Exception:
            # fallback to whatever self.db is if present
            try:
                collection = self.db
            except Exception:
                return output_dic

        row = collection.find_one({"_id": column_name})
        if not row or 'data' not in row:
            return output_dic

        data = sorted(row['data'], key=lambda x: x['unix_epoch'])
        for record in data:
            try:
                timestamp = timestamp_to_millis(record['readable_timestamp'].split(' ')[1])
            except Exception:
                # skip malformed record
                continue
            output_dic[timestamp] = record.get('value')

        return output_dic

    def format_column_name(self,column_name):
        column_name = column_name.replace('sum_','').replace(' [Mbps]','').replace('_',' ')
        word_groups = column_name.split(" ")

        
        
        
        for i in range(len(word_groups)):
            #All these words should be completely capialized like SINR
            if word_groups[i] in ['rx','ul','prb','tx','sinr','mcs']:
                word_groups[i] = word_groups[i].upper()
            else:
                word_groups[i] = word_groups[i][0].upper() + word_groups[i][1:]
        
        if 'Prbs' in word_groups:
            return 'PRB '+word_groups[0]
        
        return " ".join(word_groups)
      

    def load_csv(self, db_name='csv'):
        """
        Load graph columns from the 'csv' collection inside the 'myDatabase' DB.
        Builds self.graph_x_values and self.graph_y_values keyed by formatted names.
        """
        # Use the same DB/collection structure that database.py used:
        collection = None
        try:
            collection = self.client['myDatabase']['csv']
        except Exception:
            # as fallback try self.client[db_name] (older code paths)
            try:
                collection = self.client[db_name]
            except Exception:
                collection = None

        # raw column names that database.py wrote as _id into the csv collection
        raw_graph_columns = [
            "rx_brate uplink [Mbps]","ul_sinr",
            "sum_requested_prbs","tx_brate downlink [Mbps]",
            "ul_mcs","sum_granted_prbs"
        ]

        self.graph_x_values = {}
        self.graph_y_values = {}

        if collection is None:
            # Can't find the collection; create empty structures for all columns
            for column_name in raw_graph_columns:
                formatted = self.format_column_name(column_name)
                self.graph_x_values[formatted] = []
                self.graph_y_values[formatted] = []
        else:
            for column_name in raw_graph_columns:
                row = collection.find_one({"_id": column_name})
                formatted_name = self.format_column_name(column_name)
                if not row or 'data' not in row:
                    # no data for this column
                    self.graph_x_values[formatted_name] = []
                    self.graph_y_values[formatted_name] = []
                    continue

                data = sorted(row['data'], key=lambda x: x['unix_epoch'])
                x_list = []
                y_list = []
                for ts_rec in data:
                    try:
                        x_list.append(timestamp_to_millis(ts_rec['readable_timestamp'].split(' ')[1]))
                        y_list.append(ts_rec.get('value'))
                    except Exception:
                        # skip malformed entries
                        continue

                self.graph_x_values[formatted_name] = x_list
                self.graph_y_values[formatted_name] = y_list

        # Load other simple columns (slice_prb, scheduling_policy) from the same collection
        self.rbs_assigned = self.load_other_csv_columns(collection, 'slice_prb')
        self.scheduling_policy = self.load_other_csv_columns(collection, 'scheduling_policy')

        # update list of graph column names (formatted)
        self.graph_columns = [self.format_column_name(c) for c in raw_graph_columns]
        
    def map_scheduling_policy(self,policy):
        if policy == "":
            return

        
        return self.scheduling_policy_map[policy]
        



    def get_graph_values(self):
        return self.graph_x_values,self.graph_y_values

    def get_graph_columns(self):
        return self.graph_columns

    def get_rbs_assigned(self):
        return self.rbs_assigned
    
    def set_current_timestamp(self,timestamp):
        self.current_timestamp = timestamp

