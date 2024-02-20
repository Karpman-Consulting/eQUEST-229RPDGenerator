from itertools import islice
from rpd_generator.doe2_file_readers.model_output_reader import get_multiple_results


class BaseNode:
    """
    Base class for all nodes in the tree.
    'Node' refers to rpd_generator objects that map directly to a 229 schema data group.
    """

    boolean_map = {
        "YES": True,
        "NO": False,
    }

    def __init__(self, u_name, rmd):
        self.rmd = rmd
        self.u_name = u_name
        self.reporting_name = None
        self.notes = None
        self.keyword_value_pairs = {}

    def __repr__(self):
        return f"BaseNode('{self.u_name}')"

    def add_inputs(self, key_val_dict):
        """Insert a keyword-value pair for the BDL command."""
        self.keyword_value_pairs = key_val_dict

    def populate_data_group(self):
        """This method will be overridden by each child class"""
        return None

    def populate_data_elements(self):
        """This method will be overridden by each child class"""
        return None

    def insert_to_rpd(self, container):
        """This method will be overridden by each child class"""
        return None

    def get_obj(self, u_name):
        """
        Return the object instance by its u_name.
        :param u_name: str
        """
        return self.rmd.bdl_obj_instances.get(u_name, None)

    @staticmethod
    def get_output_data(dll_path, doe2_data_path, project_path_name, requests):
        """
        Get data from the simulation output.
        :param dll_path: (string) path to user's eQUEST D2Result.dll file included with installation files
        :param doe2_data_path: (binary string) path to DOE-2 data directory with NHRList.txt
        :param project_path_name: (binary string) path to project with project name NOT INCLUDING FILE EXTENSION
        :param requests: (dict) dictionary of description (str): (tuple) of entry_id: (int), report_key: (binary string), and row_key: (binary string)
        :return: dictionary of system data elements
        """

        chunk_size = 12  # Max number of requests to process at a time
        results = {}  # To store the reassociated keys and values

        # Split requests into chunks of at most 12
        for chunk in _chunked_dict(requests, chunk_size):
            # Extract and combine values into a list of tuples for get_multiple_results
            values_list = list(chunk.values())

            # Call the function with the current chunk of values
            chunk_results = get_multiple_results(
                dll_path, doe2_data_path, project_path_name, values_list
            )

            # Reassociate returned values with their corresponding keys
            if len(chunk_results) == len(chunk):
                results.update(zip(chunk.keys(), chunk_results))
        return results


def _chunked_dict(d, n):
    """Yield successive n-sized chunks from dictionary d."""
    it = iter(d)
    for i in range(0, len(d), n):
        yield {k: d[k] for k in islice(it, n)}
