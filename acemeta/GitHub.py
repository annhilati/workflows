import requests as WEB
import base64
import os

class Repository():
    """
    Contains the information to access a GitHub repository

    #### Arguments:
        repository (str): The repository wanted to access in the scheme `"annhilati/acemeta"`
        token (str): A PAT-Token that has access to the requested repository

    #### Methods:
        exists(): Checks if a file exists in the repository
        upload(): Uploads a file to the repository
        download(): Downloads a file from the repository
    """
    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.token = token

        self._url = f"https://api.github.com/repos/{self.repository}/contents"

    def exists(self, directory: str) -> bool:
        """
        Checks if a file already exists in the specified directory of the repository

        #### Arguments:
            directory (str): Path of the file whose existence is to be checked

        #### Raises:
            Exception: If the files existence couldn't be checked  
        """
        target = f"{self._url}/{directory}"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        response = WEB.get(target, headers=headers)
        
        if response.status_code == 200: return True
        elif response.status_code == 404: return False
        else: response.raise_for_status()

    def upload(self, file: str, directory: str, msg: str, overwrite: bool = False) -> None:
        """
        Uploads a file to the GitHub repository

        #### Arguments:
            file (str): Path to the file to upload
            directory (str): Path of the file that is to be created
            msg (str): An optional upload information displayed as the commit summary
            overwrite (bool): Whether the function is allowed to overwrite the file if it already exists

        #### Raises:
            FileExistsError: If a file with the same content already exists in the requested directory
                Carries a status_code attribute containing the HTTP status code
            Exception: For other errors encountered during download
                Carries a response.status_code attribute containing the HTTP status code
        """

        if Repository.exists(directory) and overwrite == False:
            raise FileExistsError(f"File '{self.repository}/{directory}' already exists.")
        else: 
        
            target = f"{self._url}/{directory}"
            
            with open(file, 'rb') as f:
                content = f.read()
                content_base64 = base64.b64encode(content).decode("utf-8")

            headers = {
                'Authorization': f'token {self.token}',
                'Content-Type': 'application/json'
            }
            data = {
                'message': msg,
                'content': content_base64
            }
        
            response = WEB.put(target, json=data, headers=headers)

            if response.status_code == 422:
                raise FileExistsError(f"File '{self.repository}/{directory}' already exists with the exact same content", status_code=response.status_code)
            response.raise_for_status()


    def download(self, file: str, destination: str, overwrite: bool = False) -> None:
        """
        Downloads a file from the GitHub repository.

        #### Arguments:
            file (str): Path to the file in the GitHub repository
            destination (str): Local path where the file should be saved
            overwrite (bool): Whether the function is allowed to overwrite the file if it already exists

        #### Raises:
            FileNotFoundError: If the file is not found in the repository
            FileExistsError: If a file is to be overwritten in the course of the download while the function is not allowed to do so
            Exception: For other errors encountered during download 
        """

        target = f"{self._url}/contents/{file}"
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3.raw'  # Accept header for raw content
        }
        
        response = WEB.get(target, headers=headers)
        
        if response.status_code == 404:
            raise FileNotFoundError(f"File '{file}' not found in the repository")
        response.raise_for_status()
        
        content_base64 = response.content
        content = base64.b64decode(content_base64)
        
        if os.path.exists(destination) and overwrite == False:
            raise FileExistsError(f"File '{destination}' already exists and mustn't be overwritten")
        else:
            with open(destination, 'wb') as f:
                f.write(content)