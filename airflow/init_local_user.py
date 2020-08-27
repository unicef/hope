from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser
user = PasswordUser(models.User())
user.username = "root"
user.email = "root@root.com"
user.password = "root1234"
session = settings.Session()
session.add(user)
session.commit()
session.close()