library(shiny)
library(shinydashboard)
library(rmarkdown)
library(tidyverse)
source("analiza.R", local=T)
# library(webshot)
# webshot::install_phantomjs()

# Workaround for https://github.com/yihui/knitr/issues/1538
if (packageVersion("knitr") < "1.17.3") {
  if (getRversion() > "3.4.0") {
    evaluate2 <- function(...) evaluate::evaluate(...)
    environment(evaluate2) <- asNamespace("knitr")
    knitr::knit_hooks$set(evaluate = evaluate2)
  } else {
    stop("Update knitr to run this app", call. = FALSE)
  }
}


ui <- dashboardPage(skin='green',
  dashboardHeader(title = "Geeks & Dragons"),
  dashboardSidebar(
    radioButtons('format', 'Aby pobrać raport naciśnij przycisk Download', c('HTML'),
                   inline = TRUE),
      downloadButton('downloadReport')
  ),
  dashboardBody(
    tabsetPanel(
            tabPanel("Pracownik miesiąca",
              withMathJax(),  # include the MathJax library
                selectInput('x', 'Build a regression model of mpg against:',
                choices = names(mtcars)[-1]),
              uiOutput('pracownik_miesiaca')
            ),
            tabPanel("Turniej - top 10 zawodników",
              dateRangeInput("dates_top_10", label = "Wybierz zakres dat, z którego chcesz poznać top 10 zawodników",
                 start  = "2020-01-01",
                 end    = "2023-12-31",
                 min    = "2020-01-01",
                 max    = "2023-12-31",
                 format = "mm/dd/yy",
                 separator = " - "),

              uiOutput('turniej_top_10'),
              plotlyOutput("plot_top_10_1"),
              plotlyOutput("plot_top_10_2"),
              plotlyOutput("plot_top_10_3"),
              plotlyOutput("plot_top_10_4"),
              plotlyOutput("plot_top_10_5")
            ),
            tabPanel("Dochody",
              uiOutput('dochody')
            )
          )
  )
)


# Define server logic required to draw a histogram ----
server <- function(input, output) {

  regFormula <- reactive({
    as.formula(paste('mpg ~', input$x))
  })

  output$pracownik_miesiaca <- renderUI({
    src <- normalizePath('pracownik_miesiaca.Rmd')

    tagList(
      HTML(knitr::knit2html(text = readLines(src), template = FALSE)),
      # typeset LaTeX math
      tags$script(HTML('MathJax.Hub.Queue(["Typeset", MathJax.Hub]);')),
      # syntax highlighting
      tags$script(HTML("if (hljs) $('#report pre code').each(function(i, e) {
                          hljs.highlightBlock(e)
                       });"))
    )
  })

  output$value <- renderPrint({ input$dates_top_10 })
  
  generate_plots <- function(game_id_arg) {
    data <- top_10_customers_in_general %>% filter(game_id == game_id_arg %>% as.numeric()) %>% top_n(10)
    text <- data$text_plot
    
    fig <- plot_ly(data, x = ~score, y = ~full_name, text = text,
                   type = 'bar', orientation = 'h', textposition = 'auto',
                   marker = list(color = "#44bd44"))
    fig <- fig %>% layout(title = paste0("Top 10 graczy w ", game_id_arg),
                          xaxis = list(title = ""),
                          yaxis = list(title = "", categoryorder = "total ascending"))
    
    fig
    }
  
  
  output$plot_top_10_1 <- plotly::renderPlotly({
    generate_plots(1)
  })
  output$plot_top_10_2 <- plotly::renderPlotly({
    generate_plots(2)
  })
  output$plot_top_10_3 <- plotly::renderPlotly({
    generate_plots(3)
  })
  output$plot_top_10_4 <- plotly::renderPlotly({
    generate_plots(4)
  })
  output$plot_top_10_5 <- plotly::renderPlotly({
    generate_plots(5)
  })
  

  output$turniej_top_10 <- renderUI({
    src <- normalizePath('turniej_top_10.Rmd')

    tagList(
        HTML(knitr::knit2html(text = readLines(src), template = FALSE)),
        # typeset LaTeX math
        tags$script(HTML('MathJax.Hub.Queue(["Typeset", MathJax.Hub]);')),
        # syntax highlighting
        tags$script(HTML("if (hljs) $('#report pre code').each(function(i, e) {
                            hljs.highlightBlock(e)
                        });")))
    })

    output$dochody <- renderUI({
    src <- normalizePath('dochody.Rmd')


    tagList(
        HTML(knitr::knit2html(text = readLines(src), template = FALSE)),
        # typeset LaTeX math
        tags$script(HTML('MathJax.Hub.Queue(["Typeset", MathJax.Hub]);')),
        # syntax highlighting
        tags$script(HTML("if (hljs) $('#report pre code').each(function(i, e) {
                            hljs.highlightBlock(e)
                        });"))
    )
    })


  output$downloadReport <- downloadHandler(
    filename = function() {
      paste('my-report', sep = '.', switch(
        input$format, HTML = 'html'
      ))
    },

    content = function(file) {
      src <- normalizePath('report.Rmd')

      file.copy(src, 'report.Rmd', overwrite = FALSE)

      out <- rmarkdown::render('report.Rmd', switch(
        input$format,
        HTML = html_document()
      ))
      file.rename(out, file)
    }
  )

}
# Create Shiny app ----
shinyApp(ui = ui, server = server)