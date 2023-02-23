library(tidyverse)
library(plyr)

setwd("c:/Users/BOttow/OneDrive - Rode Kruis/Türkiye/Damage_scraping/classes")
translations <- read.csv("translations2.csv", encoding = 'UTF-8')

summarizeNeighborhoodsByProvince <- function(file){
  input <- read.csv(file, encoding = 'UTF-8')
  summary <- input %>% select(c(mahalle, aciklama)) %>% table()
  dimnames(summary)$aciklama <- translations$english[match(dimnames(summary)$aciklama, translations$turkish)]
  summary <- summary %>% as.data.frame.matrix
  result <- cbind(input[match(rownames(summary), input$mahalle),c("il","ilce","mahalle")],summary)
  # 
  # write.csv(result, sprintf('summary_%d.csv', province), row.names = F)
}

files <- list.files(pattern = "output_province")
file <- files[1]
result <- summarizeNeighborhoodsByProvince(file)
for (i in 2:length(files)){
  print(i)
  file <- files[i]
  result2 <- summarizeNeighborhoodsByProvince(file)
  result <- rbind.fill(result,result2)
  result[is.na(result)] <- 0
}


neighborhood_shapes <- "c:/Users/BOttow/OneDrive - Rode Kruis/Türkiye/GIS/data/admin_areas/tur_polbnda_adm3_Southeast.shp"

library (sf)
shapes <- st_read(neighborhood_shapes)
lookup <- read.csv("lookuptable.csv", encoding = 'UTF-8')
names(lookup)[1] <- "mahalleId"
joined <- left_join(result,lookup, by = c("mahalle" = "ad", "ilce" = "district_name", "il" = "province_name"))
match(shapes$adm3, joined$adm3)
shapes[,translations$english] <- joined[match(shapes$adm3, joined$adm3),translations$english]
st_write(shapes, dsn = "../geodata/damage.gpkg", layer = "provinces")
