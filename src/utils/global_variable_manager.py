import threading
import datetime
import uuid

class GlobalVariableManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GlobalVariableManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.global_list_data_profiles = []
            self.global_list_data_profiles_temp = []
            self.global_list_data_auto = []
            self.global_list_data_auto_temp = []
            self.global_profiles_selected = []
            self.global_auto_selected = []
            self.global_data_auto_profiles_temp = []
            self.global_data_query_id_temp = []
            self.global_config_common = {}

            self.lock_list_data_profiles = threading.Lock()
            self.lock_list_data_auto = threading.Lock()
            self.lock_profiles_selected = threading.Lock()
            self.lock_auto_selected = threading.Lock()
            self.lock_list_data_profiles_temp = threading.Lock()
            self.lock_list_data_auto_temp = threading.Lock()
            self.lock_data_auto_profiles_temp = threading.Lock()
            self.lock_data_query_id_temp = threading.Lock()

            self._initialized = True

    def update_object(self, existing_object, new_data):
        """Update fields in existing_object with new_data."""
        for key, value in new_data.items():
            existing_object[key] = value

    def find_index_of_object(self, existing_list, new_object):
        """Find index of object in existing_list based on 'id'."""
        for i, obj in enumerate(existing_list):
            if obj.get('id') == new_object.get('id'):
                return i
        return None
    
    def update_list(self, existing_list, new_data, lock):
        """Generic function to update a list with new data."""
        with lock:
            if isinstance(new_data, list):
                for item in new_data:
                    index = self.find_index_of_object(existing_list, item)
                    if index is not None:
                        self.update_object(existing_list[index], item)
                    else:
                        existing_list.append(item)
            else:
                index = self.find_index_of_object(existing_list, new_data)
                if index is not None:
                    self.update_object(existing_list[index], new_data)
                else:
                    existing_list.append(new_data)
    
    def get_list(self, lock, list_reference):
        """Generic function to safely return a list under a lock."""
        with lock:
            return list_reference

    def set_list(self, lock, list_reference, data):
        """Generic function to safely set or add to a list under a lock."""
        with lock:
            if isinstance(data, list):
                list_reference[:] = data  # Clear and set the list
            else:
                if data not in list_reference:
                    list_reference.append(data)
    
    def remove_from_list_by_id(self, lock, list_reference, id_key='id', remove_id=''):
        """Generic function to remove an item from list based on an 'id' key."""
        with lock:
            if remove_id:
                list_reference[:] = [item for item in list_reference if item.get(id_key) != remove_id]
            else:
                list_reference.clear()

    # Profiles-related methods
    def get_global_list_data_profiles(self):
        return self.get_list(self.lock_list_data_profiles, self.global_list_data_profiles)

    def set_global_list_data_profiles(self, data):
        self.set_list(self.lock_list_data_profiles, self.global_list_data_profiles, data)

    def update_global_list_data_profiles(self, data):
        self.update_list(self.global_list_data_profiles, data, self.lock_list_data_profiles)

    def get_global_list_data_profiles_temp(self):
        return self.get_list(self.lock_list_data_profiles_temp, self.global_list_data_profiles_temp)

    def set_global_list_data_profiles_temp(self, data):
        self.set_list(self.lock_list_data_profiles_temp, self.global_list_data_profiles_temp, data)

    def update_global_list_data_profiles_temp(self, data):
        self.update_list(self.global_list_data_profiles_temp, data, self.lock_list_data_profiles_temp)
    
    # Selected profiles methods
    def get_global_profiles_selected(self):
        return self.global_profiles_selected

    def set_global_profiles_selected(self, profiles):
        """Set or add profiles to global_profiles_selected."""
        with self.lock_profiles_selected:
            if isinstance(profiles, list):
                current_ids = {profile['id'] for profile in self.global_profiles_selected}   
                new_profiles = [profile for profile in profiles if profile['id'] not in current_ids]   
                self.global_profiles_selected.extend(new_profiles)   
            else:
                # Handle case where a single profile is passed, not a list
                if profiles['id'] not in {profile['id'] for profile in self.global_profiles_selected}:
                    self.global_profiles_selected.append(profiles)

    def remove_global_profiles_selected(self, profile):
        self.remove_from_list_by_id(lock=self.lock_profiles_selected, list_reference=self.global_profiles_selected, id_key='id', remove_id=profile)
        
    def clear_global_profiles_selected(self):
        with self.lock_profiles_selected:
            self.global_profiles_selected.clear()

    # Auto-related methods
    def get_global_list_data_auto(self):
        return self.get_list(self.lock_list_data_auto, self.global_list_data_auto)

    def set_global_list_data_auto(self, data):
        self.set_list(self.lock_list_data_auto, self.global_list_data_auto, data)

    def update_global_list_data_auto(self, data):
        self.update_list(self.global_list_data_auto, data, self.lock_list_data_auto)

    def get_global_list_data_auto_temp(self):
        return self.get_list(self.lock_list_data_auto_temp, self.global_list_data_auto_temp)

    def set_global_list_data_auto_temp(self, data):
        self.set_list(self.lock_list_data_auto_temp, self.global_list_data_auto_temp, data)

    def update_global_list_data_auto_temp(self, data):
        self.update_list(self.global_list_data_auto_temp, data, self.lock_list_data_auto_temp)

    # Config common methods
    def get_global_config_common(self):
        return self.global_config_common
    
    def update_global_config_common(self, new_config):
        self.global_config_common.update(new_config)
        return self.global_config_common
    
    # Selected auto methods
    def get_global_auto_selected(self):
        return self.global_auto_selected

    def set_global_auto_selected(self, auto):
        """Set or add auto to global_auto_selected."""
        with self.lock_auto_selected:
            if isinstance(auto, list):
                current_ids = {item['id'] for item in self.global_auto_selected}  
                new_auto = [item for item in auto if item['id'] not in current_ids]  
                self.global_auto_selected.extend(new_auto)  
            else:
                # Handle case where a single auto is passed, not a list
                if auto['id'] not in {item['id'] for item in self.global_auto_selected}:
                    self.global_auto_selected.append(auto)

    def remove_global_auto_selected(self, auto):
        self.remove_from_list_by_id(lock=self.lock_auto_selected, list_reference=self.global_auto_selected, id_key='id', remove_id=auto)
        
    def clear_global_auto_selected(self):
        with self.lock_auto_selected:
            self.global_auto_selected.clear()

    # Temporary data auto profiles methods
    def get_global_data_auto_profiles_temp(self):
        return self.get_list(self.lock_data_auto_profiles_temp, self.global_data_auto_profiles_temp)

    def update_global_data_auto_profiles_temp(self, data):
        with self.lock_data_auto_profiles_temp:
            if isinstance(data, list):
                for item in data:
                    index = self.find_index_of_object(self.global_data_auto_profiles_temp, item)
                    item['id'] = str(uuid.uuid4())
                    item['last_updated'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    if index is not None:
                        self.update_object(self.global_data_auto_profiles_temp[index], item)
                    else:
                        self.global_data_auto_profiles_temp.append(item)
            else:
                index = self.find_index_of_object(self.global_data_auto_profiles_temp, data)
                data['id'] = str(uuid.uuid4())
                data['last_updated'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                if index is not None:
                    self.update_object(self.global_data_auto_profiles_temp[index], data)
                else:
                    self.global_data_auto_profiles_temp.append(data)

    def clear_global_data_auto_profiles_temp(self):
        with self.lock_data_auto_profiles_temp:
            self.global_data_auto_profiles_temp.clear()
        
    # Query ID methods
    def get_global_data_query_id_temp(self):
        return self.get_list(lock=self.lock_data_query_id_temp, list_reference=self.global_data_query_id_temp)
    
    def append_global_data_query_id_temp(self, data):
        self.set_list(self.lock_data_query_id_temp, self.global_data_query_id_temp, data)
    
    def clear_global_data_query_id_temp(self):
        with self.lock_data_query_id_temp:
            self.global_data_query_id_temp.clear()