install.packages("RMariaDB")
library(RMariaDB)
library(tidyverse)
library(dbplyr)

con_mariadb <- dbConnect(RMariaDB::MariaDB(),
                dbname = 'team03',
                username = 'team03',
                password = "te@m0e",
                host = "giniewicz.it")

score <- tbl(con_mariadb, "score")

