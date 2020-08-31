# Introduction
Inspired by the AWS SDK for .NET Core, this tries to implement a simple way to retrieve secret
key-value pairs from Parameter Store inside Systems Manager in AWS.

# Usage
```python
from secrets import Secrets

secrets = Secrets("Application/Environment")
password = secrets.get("Database/Password")
```