raport.html: Raport/raport.Rmd
	Rscript -e "rmarkdown::render('Raport/raport.Rmd', output_format = 'html_document')"
	
.PHONY: open
open:
ifeq ($(wildcard Raport/raport.html),)
	@echo "Plik report.html nie istnieje. Generowanie pliku..."
	make raport.html
	cmd /c start Raport/raport.html
else
	@echo "Otwieranie pliku report.html..."
	cmd /c start Raport/raport.html
endif
