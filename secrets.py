import boto3
from botocore.exceptions import ClientError
from exceptions import (
    FailedSecretsRequestException,
    SecretPathNotFoundException,
)


class Secrets:
    """
    Class to hold secrets from SSM parameter store in AWS

    Attributes
    ----------
    secrets
    _secrets : dict
        The secrets as an nested dictionary
    _path : string
        The path to extract from ssm (all sub-paths will be extracted recursively)
    """

    def __init__(self, path):
        """
        Upon instantiation, downloads and decrypts the secrets from SSM given the path.

        Parameters
        ----------
        path : string
            The base path to extract. Optional to have a leading "/". All secrets below this path
            will be extracted.
        """
        self._path = "/" + path.strip("/") + "/"
        self._secrets = self._request_secrets()
        self._secret_list_to_dict()

    def _request_secrets(self):
        """
        Downloads the secrets given the path from SSM in AWS

        Returns
        -------
        list
            List of "Parameters" from SSM

        Raises
        ------
        FailedSecretsRequestException
            The request for the secrets failed
        """
        try:
            client = boto3.client("ssm")
            secrets = client.get_parameters_by_path(
                Path=self._path, WithDecryption=True, Recursive=True
            )
        except ClientError as e:
            raise FailedSecretsRequestException(f"Failed to retrieve secrets: {repr(e)}.")
        return secrets["Parameters"]

    def _secret_list_to_dict(self):
        def remove_path_prefix(x):
            return x.replace(self._path, "", 1)

        self._secrets = {
            remove_path_prefix(secret["Name"]): secret["Value"] for secret in self._secrets
        }

    @property
    def secrets(self):
        """
        All of the secrets as a dictionary

        Returns
        -------
        dict
            Dictionary of all of the secrets in self._path
        """
        return self._secrets

    def get(self, secret_path):
        """
        Gets the secret at the "/"-separated path

        Parameters
        ----------
        secret_path : string
            Path to the secret, separated by sep

        Returns
        -------
        string
            The secret value

        Raises
        ------
        SecretPathNotFoundException
            If there is no secret at the given path
        """

        try:
            secret = self._secrets[secret_path]
        except (KeyError, TypeError):
            raise SecretPathNotFoundException(f"The secret {secret_path} was not found.")

        return secret
