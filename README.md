# Ninjabot

A personal Discord bot I made as a fun project.

## Installation

First, clone the repository:
```
$ git clone https://github.com/Ninjaclasher/Ninjabot
$ cd Ninjabot
```

Install the prerequisites:
```bash
$ apt update
$ apt install mariadb-server git python3
```

```bash
$ pip install -r requirements.txt
```

As well, create the database and load the tables:
```mysql
$ mysql -uroot -p
MariaDB> CREATE DATABASE ninjabot DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
MariaDB> GRANT ALL PRIVILEGES ON ninjabot.* to 'ninjabot'@'localhost' IDENTIFIED BY '<password>';
MariaDB> exit
$ mysql -uroot -p ninjabot < ninjabot.sql
```

Finally, create the necessary files:
```bash
$ touch local_settings.py
```


## Usage

Add any settings to `local_settings.py` that differ from `settings.py`. In particular, you should add the bot `TOKEN`, and MySQL credentials.

```bash
$ python3 main.py
```

