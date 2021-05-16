# remove old tmp files
rm *.aux
rm *.log
pdflatex data_report.tex
# build twice to make sure all references are ok
pdflatex data_report.tex
