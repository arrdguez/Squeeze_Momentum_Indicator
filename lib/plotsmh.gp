
reset
set terminal pdfcairo font "Times" square size 35,7 
set output 'graph_smh.pdf'



set xlabel 'time'
set ylabel 'price'


plot 'smh_1h.csv' u 1:2  w lines lc 'green' title "1H",\
     'smh_4h.csv' u 1:2  w lines lc 'blue' title "4H",\
     1 lc 'black' notitle
