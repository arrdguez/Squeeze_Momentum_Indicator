
reset
set terminal pdfcairo font "Times" square size 35,7 
set output 'graph.pdf'



set xlabel 'time'
set ylabel 'price'

set multiplot layout 3,1
plot 'df.csv' u 1:3:5:4:6  w candlesticks notitle

plot 'dfTem.csv' u 1:7  w impulses lc 'blue' notitle



plot 'dfTem.csv' u 1:8 w impulses notitle
unset multiplot 
