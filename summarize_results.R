library(tidyverse)

setwd("c:/Users/BOttow/OneDrive - Rode Kruis/Türkiye/Damage_scraping/classes")

names_english <- c("To be demolished urgently", "heavy damage", "light damage", "locked, not accessible",
                   "excluded from assessment", "no damage", "not assessed", "collapsed")

summarizeNeighborhoodsByProvince <- function(province){
  input <- read.csv(sprintf("output_province_%d.csv", province), encoding = 'UTF-8')
  summary <- input %>% select(c(mahalle, aciklama)) %>% table()
  dimnames(summary)$aciklama <- names_english
  summary <- summary %>% as.data.frame.matrix
  result <- cbind(input[match(rownames(summary), input$mahalle),c("il","ilce","mahalle")],summary)
  # 
  # write.csv(result, sprintf('summary_%d.csv', province), row.names = F)
}

province <- 2
result <- summarizeNeighborhoodsByProvince(province)

neighborhood_shapes <- "c:/Users/BOttow/OneDrive - Rode Kruis/Türkiye/GIS/data/admin_areas/tur_polbnda_adm3_Southeast.shp"

library (sf)
shapes <- st_read(neighborhood_shapes)
lookup <- read.csv("lookuptable.csv", encoding = 'UTF-8')
joined <- left_join(result,lookup, by = c("mahalle" = "ad", "ilce" = "district_name", "il" = "province_name"))
match(shapes$adm3, joined$adm3)
shapes[,names_english] <- joined[match(shapes$adm3, joined$adm3),names_english]
st_write(shapes, dsn = "../geodata/damage.gpkg", layer = "province2")
