# install.packages("plotly")
library(RMariaDB)
library(tidyverse)
library(dbplyr)
library(plotly)

con_mariadb <- dbConnect(RMariaDB::MariaDB(),
                dbname = 'team03',
                username = 'team03',
                password = "te@m0e",
                host = "giniewicz.it")

score <- tbl(con_mariadb, "score") %>%
        collect()

tournament <- tbl(con_mariadb, "tournament") %>%
        select(game_id, tournament_id, tournament_date) %>%
        collect()

customer <- tbl(con_mariadb, "customer") %>%
        select(first_name, last_name, customer_id) %>%
        collect()

game <- tbl(con_mariadb, "game") %>%
        select(game_id, game_title) %>%
        collect()


# 10 z najlepszym score dla każdej grupy (zwraca więcej niż 10, bo remisy)
score_tournament <- left_join(score, tournament, by = c("tournament_id")) %>%
    group_by(game_id) %>%
    slice_max(score, n = 10) %>%
    select(!c(score_id))


### join
# join z customer by customer_id, żeby wiedzieć kto ma jakiego score
top_10_customers_in_general <- left_join(score_tournament, customer, by=c("customer_id")) %>%
        select(!c(customer_id))

# join z game by game_id żeby wiedzieć jaki tytuł miała gra


top_10_customers_in_general <- top_10_customers_in_general %>% mutate(full_name = str_c(first_name, " ", last_name))
top_10_customers_in_general <- top_10_customers_in_general %>% mutate(text_plot = str_c("score: ", score, " - ", tournament_date))


### plots
generate_plots <- function(data_arg, game_id_arg){
        data <- data_arg %>% filter(game_id == game_id_arg %>% as.numeric()) %>% top_n(10)
        text <- data$text_plot

        fig <- plot_ly(data, x = ~score, y = ~full_name, text = text,
                type = 'bar', orientation = 'h', textposition = 'auto',
                marker = list(color = "#44bd44"))
        fig <- fig %>% layout(title = paste0("Top 10 graczy w ", game_id_arg),
                xaxis = list(title = ""),
                yaxis = list(title = "", categoryorder = "total ascending"))

        fig
}

# top_10_grouped <- top_10_customers_in_general %>% group_by(game_id) %>% tally()
# for (i in top_10_grouped$game_id){
#         generate_plots(data_arg = top_10_customers_in_general, game_id_arg = i)  
# }
