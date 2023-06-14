library(shiny)
library(shinythemes)
library(shinydashboard)
library(rmarkdown)

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
  dashboardHeader(title = "Gametopia Rentals"),
  dashboardSidebar(
    radioButtons('format', 'Document format', c('HTML'),
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
              uiOutput('turniej_top_10')
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

  output$turniej_top_10 <- renderUI({
    src <- normalizePath('turniej_top_10.Rmd')

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