import json
import os
import shutil
import threading
from cryptography.fernet import Fernet
import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox
from .global_variable_manager import GlobalVariableManager

class FileManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FileManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.file_lock = threading.Lock()
        self.global_variable = GlobalVariableManager()

    """Create Manager File"""
    def file_exists(self, path: str, create_if_missing: bool = False, is_directory: bool = False) -> bool:
        if is_directory:
            if os.path.isdir(path):
                return True
            elif create_if_missing:
                os.makedirs(path, exist_ok=True)
                return True
            return False
        else:
            if os.path.isfile(path):
                return True
            elif create_if_missing:
                with open(path, 'w', encoding='utf-8'):
                    pass  # Just create an empty file
                return True
            return False

    def show_warning(self, title: str, message: str) -> None:
        QMessageBox.warning(None, title, message)

    def get_file_path(self, parent: None= None, file_dialog_filter: str = "Excel and Text Files (*.xlsx *.xls *.txt)", file_dialog_mode: QFileDialog.FileMode = QFileDialog.FileMode.ExistingFiles, 
                      ) -> str:
        file_dialog = QFileDialog(parent)
        file_dialog.setFileMode(file_dialog_mode)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_dialog.setNameFilter(file_dialog_filter)
        if file_dialog.exec():
            return os.path.normpath(file_dialog.selectedFiles()[0])
        return ""

    def create_file(self, folder_path: str, file_type: str, content: any) -> None:
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f'data.{file_type}')

        if file_type == 'xlsx':
            df = pd.DataFrame(content)
            df.to_excel(file_path, index=False)
        elif file_type == 'txt':
            with open(file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(content)
        else:
            print(f"Unsupported file type: {file_type}. Choose 'xlsx' or 'txt'.")
        print(f"File created at: {file_path}")

    def move_file(self, file_path: str, target_path: str) -> None:
        if self.file_exists(file_path):
            shutil.move(file_path, target_path)
        else:
            print(f"File not found: {file_path}")

    def rename_file(self, file_path: str, new_name: str) -> None:
        if self.file_exists(file_path):
            new_file_path = os.path.join(os.path.dirname(file_path), new_name)
            shutil.move(file_path, new_file_path)
            print(f"File renamed to {new_name}")
        else:
            print(f"File not found: {file_path}")
    
    def remove_file(self, file_path: str) -> bool:
        if not self.file_exists(file_path):
            self.show_warning("Path Error", f"File '{file_path}' not found.")
            return False
        os.remove(file_path)
        return True
    
    def get_files_in_directory(self, path: str, extensions: list[str] | None = None) -> list[str]:
        try:
            if not os.path.isdir(path):
                self.show_warning("Path Error", f"Directory '{path}' not found.")
                return []

            if extensions is None:
                files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            else:
                files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and any(f.endswith(ext) for ext in extensions)]

            return files
        except Exception as e:
            print(f"get_files_in_directory Error {e}")
            return []

    def read_file_text(self, file_path: str, read_list_file: bool = False) -> str | list[str] | None:
        with self.file_lock:
            if not self.file_exists(file_path):
                self.show_warning("Path Error", f"File '{file_path}' not found.")
                return None
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read() if not read_list_file else file.readlines()
            except Exception as e:
                print(f"read_file_text Error: {e}")
                return None

    def read_file_excel(self, file_path: str, sheet_name: str | int = 0, columns: list[int] | None = None) -> str | None:
        with self.file_lock:
            if not self.file_exists(file_path):
                self.show_warning("Path Error", f"File '{file_path}' not found.")
                return None
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, header=None)
                
                if columns is not None:
                    df = df[columns]
                
                return df.to_string(index=False, header=False)
            except Exception as e:
                print(f"read_file_excel Error: {e}")
                return None

    def copy_and_replace_file_content(self, src_path: str, dst_path: str, is_replace: bool = False) -> None:
        with self.file_lock:
            if not self.file_exists(src_path):
                self.show_warning("File Error", f"File '{src_path}' not found.")
                return
            try:
                with open(src_path, 'r', encoding='utf-8') as src_file:
                    content = src_file.read()
                mode = 'w' if is_replace else 'a'
                with open(dst_path, mode, encoding='utf-8') as dst_file:
                    dst_file.write(content)
            except Exception as e:
                print(f"copy_and_replace_file_content Error: {e}")

    def copy_and_replace_file(self, source_file: str, destination_file: str) -> None:
        if not self.file_exists(source_file):
            self.show_warning("File Error", f"File '{source_file}' not found.")
            return
        shutil.copy2(source_file, destination_file)

    def remove_whitespace_in_file_name(self, file_path: str) -> str | None:
        try:
            directory, filename = os.path.split(file_path)
            new_file_path = os.path.join(directory, filename.replace(" ", ""))
            os.rename(file_path, new_file_path)
            return new_file_path
        except Exception as e:
            print(f"remove_whitespace_in_file_name Error: {e}")
            return None

    """Create Manager Folder"""
    def get_folder_path(self) -> str:
        return self.get_file_path(None, "Select Folder", QFileDialog.FileMode.Directory)

    def remove_folder(self, folder_path: str) -> bool:
        if not os.path.isdir(folder_path):
            self.show_warning("Path Error", f"Folder '{folder_path}' not found.")
            return False
        shutil.rmtree(folder_path)
        return True
    
    def move_folders(self, source_folder: str, destination_folder: str) -> bool:
        try:
            if not self.file_exists(source_folder):
                self.show_warning("Path Error", f"Error: Source folder '{source_folder}' does not exist.")
                return False
            if not self.file_exists(destination_folder):
                os.makedirs(destination_folder)
            for item in os.listdir(source_folder):
                source_item = os.path.join(source_folder, item)
                if self.file_exists(source_item):
                    shutil.move(source_item, destination_folder)
                    self.show_warning("Success", f"Folder '{item}' moved to '{destination_folder}' successfully.")
            return True
        except Exception as e:
            print(f"move_folders Error {e}")
            return False

    def list_directories_in_directory(self, directory: str = '') -> list[str]:
        if not self.file_exists(directory):
            self.show_warning("Path Error", f"Directory '{directory}' not found.")
            return []
        return [os.path.join(directory, item) for item in os.listdir(directory) if self.file_exists(os.path.join(directory, item))]
    
    def list_specific_files_in_directory(self, directory: str, file_name: str) -> list[str]:
        try:
            specific_files = []
            if not self.file_exists(directory):
                self.show_warning("Path Error", f"Directory '{directory}' not found.")
                return specific_files
            for root, dirs, files in os.walk(directory):
                for file_name_in_dir in files:
                    if file_name_in_dir == file_name:
                        specific_files.append(os.path.join(root, file_name_in_dir))
            return specific_files
        except Exception as e:
            print(f"list_specific_files_in_directory Error {e}")
            return []

    """Create Manager file config"""
    def _write_data_to_file(self, data: any, filename: str, folder: str, mode: str = 'w') -> None:
        with self.file_lock:
            try:
                file_path = os.path.join(os.getcwd(), folder, f'{filename}')
                with open(file_path, mode, encoding='utf-8') as file:
                    if mode == 'w':
                        json.dump(data, file)
                    else:
                        file.write(data)
            except Exception as e:
                print(f"Error in _write_data_to_file: {e}")

    def save_data_to_file(self, data: any, filename: str = 'data.txt', folder: str = 'data') -> None:
        self._write_data_to_file(data, filename, folder, mode='w')

    def append_data_to_file(self, data: any, filename: str = 'data.txt', folder: str = 'data') -> None:
        self._write_data_to_file(data, filename, folder, mode='a')

    def save_data_to_config_folder(self, data: any, filename: str = 'config', folder: str = 'data') -> None:
        with self.file_lock:
            try:
                directory = os.path.join(os.getcwd(), folder)
                os.makedirs(directory, exist_ok=True)
                file_path = os.path.join(directory, f'{filename}.json')
                old_data = {}
                if self.file_exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        old_data = json.load(file)
                old_data.update(data)
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(old_data, file)
            except Exception as e:
                print(f"save_data_to_config_folder Error {e}")

    def load_data_from_config_folder(self, filename: str = 'config', folder: str = 'data', key: str | None = None) -> any:
        with self.file_lock:
            file_path = os.path.join(os.getcwd(), folder, f'{filename}.json')
            if not self.file_exists(file_path):
                return None
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data.get(key) if key else data
        
    def update_key_value_in_config_file(self, key: str, new_value: any, filename: str = 'config', folder: str = 'data') -> None:
        with self.file_lock:
            file_path = os.path.join(os.getcwd(), folder, f'{filename}.json')
            if not self.file_exists(file_path):
                self.show_warning("Path Error", f"Directory '{filename}' not found.")
            try:
                with open(file_path, "r", encoding='utf-8') as file:
                    config_data = json.load(file)

                if key in config_data:
                    config_data[key] = new_value

                    with open(file_path, "w", encoding='utf-8') as file:
                        json.dump(config_data, file)
                else:
                    self.show_warning("Update Error", f"Not find '{key}' in {filename}. Nothing has changed")

            except Exception as e:
                print("update_key_value_in_config_file Error", f"File '{filename}' has errors: {e}")
                
    def get_data_from_file_data_by_profile_and_auto_id(self, profile_id: str = '', auto_id: str = '', filename: str = 'data_auto_profiles', folder: str = 'data') -> any:
        """
        Retrieve data from the specified JSON file based on profile_id and auto_id.
        Returns the first matching object or None if not found.
        """
        with self.file_lock:
            file_path = os.path.join(os.getcwd(), folder, f'{filename}.json')
            self.file_exists(file_path, True)

            # Read the existing data from the file
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    existing_data = json.load(file)
            except json.JSONDecodeError:
                print(f"Error: {file_path} contains invalid JSON. Resetting file content.")
                existing_data = []
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(existing_data, file)

            if profile_id and auto_id:
                return next((obj for obj in existing_data if obj.get('profile_id') == profile_id and obj.get('auto_id') == auto_id), None)
            return existing_data
        
    def append_data_to_file_data(self, filename: str = 'data_auto_profiles', folder: str = 'data') -> None:
        with self.file_lock:
            file_path = os.path.join(os.getcwd(), folder, f'{filename}.json')
            if not self.file_exists(file_path):
                # If the file doesn't exist, create it and write an empty list
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump([], file, indent=4)

            # Read the existing data from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []

            # Prepare a dictionary for quick lookups
            existing_data_dict = {(obj.get('profile_id'), obj.get('auto_id')): obj for obj in existing_data}

            # Update or append the new data from the temporary list
            for new_data in self.global_variable.get_global_data_auto_profiles_temp():
                key = (new_data.get('profile_id'), new_data.get('auto_id'))
                existing_data_dict[key] = new_data

            # Convert the dictionary back to a list
            updated_data = list(existing_data_dict.values())

            # Write the updated data back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(updated_data, file, indent=4)

            # Clear the temporary data after saving to the file
            self.global_variable.clear_global_data_auto_profiles_temp()
    
    def append_data_query_id_to_file(self, filename: str = 'data_query_id', folder: str = 'data', is_append: bool = False) -> None:
        with self.file_lock:
            file_path = os.path.join(os.getcwd(), folder, f'{filename}.txt')
            
            # Nếu file không tồn tại, tạo mới và ghi dữ liệu trống vào
            if not self.file_exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write('')
                    
            if is_append:
                # Mở file ở chế độ ghi thêm (append)
                with open(file_path, 'a', encoding='utf-8') as file:
                    data_to_append = self.global_variable.get_global_data_query_id_temp()

                    # Append data mới vào file, mỗi item là một dòng
                    for item in data_to_append:
                        file.write(f"{item}\n")
                        
            else:
                # Mở file ở chế độ ghi (xóa dữ liệu cũ và ghi mới)
                with open(file_path, 'w', encoding='utf-8') as file:
                    data_to_append = self.global_variable.get_global_data_query_id_temp()

                    # Ghi đè dữ liệu mới vào file
                    for item in data_to_append:
                        file.write(f"{item}\n")

            # Xóa dữ liệu tạm sau khi ghi vào file
            self.global_variable.clear_global_data_query_id_temp()
 
    """Create Manager file zip"""
    # def extractZip(self):
    #     with zipfile.ZipFile(self.profile_zip_path, 'r') as zip_ref:
    #         zip_ref.extractall(self.profile_path)
    #     os.remove(self.profile_zip_path)
        
    # def zipdir(self, path_out, path, ziph):
    #     for root, dirs, files in os.walk(path):
    #         for file in files:
    #             path = os.path.join(root, file)
    #             if stat.S_ISSOCK(os.stat(path).st_mode):
    #                 continue
    #             try:
    #                 ziph.write(path, path.replace(path_out, ''))
    #             except:
    #                 continue

    """Create Manager file encrypt"""
    def generate_key_or_load_key_encrypt_cookie(self) -> bytes:
        key_file_path = os.path.join(os.getcwd(), 'src', 'data', 'config', 'key.key')
        try:
            with open(key_file_path, 'rb') as key_file:
                return key_file.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file_path), exist_ok=True)
            with open(key_file_path, 'wb') as key_file:
                key_file.write(key)
            return key
        
    def encrypt_content(self, content: any) -> bytes | None:
        key = self.generate_key_or_load_key_encrypt_cookie()
        try:
            f = Fernet(key)
            encrypted_content = f.encrypt(json.dumps(content).encode())
            return encrypted_content
        except Exception as e:
            print(f"encrypt_content Error {e}")
            return None

    def decrypt_content(self, encrypted_content: bytes) -> any:
        key = self.generate_key_or_load_key_encrypt_cookie()
        try:
            f = Fernet(key)
            decrypted_content = f.decrypt(encrypted_content).decode()
            return json.loads(decrypted_content)
        except Exception as e:
            print(f"decrypt_content Error {e}")
            return None
