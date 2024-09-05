import re
import copy


def make_ids_unique(data, seen_ids=None, id_counters=None, visited=None, parent=None, key=None):
    if seen_ids is None:
        seen_ids = {}
    if id_counters is None:
        id_counters = {}
    if visited is None:
        visited = set()

    if isinstance(data, dict):
        obj_id = id(data)

        if obj_id in visited:
            if parent is not None and key is not None:
                data_copy = copy.deepcopy(data)
                parent[key] = data_copy
                data = data_copy
                obj_id = id(data)
            else:
                return

        visited.add(obj_id)

        if 'id' in data:
            current_id = data['id']

            if current_id in seen_ids:
                match = re.search(r'--(\d+)$', current_id)
                if match:
                    number = int(match.group(1)) + 1
                    unique_id = re.sub(r'--\d+$', f"--{number}", current_id)
                else:
                    seen_ids[current_id] += 1
                    unique_id = f"{current_id}--{seen_ids[current_id]}"

                while unique_id in seen_ids:
                    match = re.search(r'--(\d+)$', unique_id)
                    if match:
                        number = int(match.group(1)) + 1
                        unique_id = re.sub(r'--\d+$', f"--{number}", unique_id)

                data['id'] = unique_id
                seen_ids[unique_id] = 0
            else:
                seen_ids[current_id] = 0

        keys_to_remove = []
        for k, value in list(data.items()):
            if isinstance(value, dict):
                make_ids_unique(value, seen_ids, id_counters, visited, parent=data, key=k)
                if not value:
                    keys_to_remove.append(k)
            elif isinstance(value, list):
                make_ids_unique(value, seen_ids, id_counters, visited, parent=data, key=k)

        for k in keys_to_remove:
            del data[k]

    elif isinstance(data, list):
        items_to_remove = []
        for index, item in enumerate(data):
            if isinstance(item, dict):
                make_ids_unique(item, seen_ids, id_counters, visited, parent=data, key=index)
                if not item:
                    items_to_remove.append(item)
            elif isinstance(item, list):
                make_ids_unique(item, seen_ids, id_counters, visited, parent=data, key=index)

        for item in items_to_remove:
            data.remove(item)
