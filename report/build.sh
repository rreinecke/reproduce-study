# remove old tmp files
rm *.aux
rm *.log

[ "$(ls -A ../figs)" ] && echo "Found figures" || echo "Figures not found! Run the plotting script first"

pdflatex data_report.tex
# build twice to make sure all references are ok
pdflatex data_report.tex
