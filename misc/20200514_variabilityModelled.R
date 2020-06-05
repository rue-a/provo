# @prov.init
# @prov.author lukasEgli
# @prov.organization ufz


#### load packages
library(raster)
library(rgdal)
library(car)
library(varhandle)
library(tidyr)

###### prepare crop growing calendar

setwd("C:/Users/egli/Nextcloud/Cloud/GeoKur/UseCases/1/Data/GrowingSeason")

# @prov.description overlay2growingMonths create a raster for each month that shows regions where a given crop can be grown during that month 
overlay2growingMonths <- function(plant,tot) {
  stack(
    lapply(c(31,59,90,120,151,181,212,243,273,304,334,365),function(t){
     overlay(plant,tot,fun=function(x1,y1){ifelse((((x1+y1<365&x1<=t&x1+y1>t)|(x1+y1>365&(t>x1|t<=(x1+y1-365))))),1,NA)})
    })
  )
}
# @prov.unit stackMaize = overlay2growingMonths(maize.plant.asc,maize.tot.days.asc) semanticShift
stackMaize <- overlay2growingMonths(raster("maize.plant.asc"),raster("maize.tot.days.asc"))
# @prov.unit stackWheat = overlay2growingMonths(wheat.plant.asc,wheat.tot.days.asc) semanticShift
stackWheat <- overlay2growingMonths(raster("wheat.plant.asc"),raster("wheat.tot.days.asc"))
# @prov.unit stackRice = overlay2growingMonths(rice.plant.asc,rice.tot.days.asc) semanticShift 
stackRice <- overlay2growingMonths(raster("rice.plant.asc"),raster("rice.tot.days.asc"))
# @prov.unit stackSoybeans = overlay2growingMonths(soybeans.plant.asc,soybeans.tot.days.asc) semanticShift 
stackSoybeans <- overlay2growingMonths(raster("soybeans.plant.asc"),raster("soybeans.tot.days.asc"))

###### prepare historical cropland 

setwd("C:/Users/egli/Nextcloud/Cloud/PhD_Leipzig/Publications/Globalization/datasetsPreparation/all/CroplandAge/Original/Cropland")

# @prov.description stack creates RasterStack from individual rasters
# @prov.unit stackCropland = stack(cropland1980AD.asc,cropland1990AD.asc,cropland2000AD.asc,cropland2010AD.asc) basalChange
stackCropland <- stack(list(raster("cropland1980AD.asc"),raster("cropland1990AD.asc"),raster("cropland2000AD.asc"),raster("cropland2010AD.asc")))

# @prov.description reclassifyCropland reclass cells with croplands to 1 and without to NA
reclassifyCropland <- function(stackCrop){
  stackCrop[stackCrop>0] <- 1
  stackCrop[stackCrop<=0] <- NA   
  stackCrop
}
# @prov.unit stackCroplandBinary = reclassifyCropland(stackCropland) valueChange
stackCroplandBinary <- reclassifyCropland(stackCropland)


############ mask monthly climate data by cropland and month, calculate mean climate per year and extract by political units
## political units
NUTS2_shape <- readOGR("C:/Users/egli/Nextcloud/Cloud/PhD_Leipzig/ESCALATE/ARAGOG/shapes/NUTS2/NUTS_RG_01M_2013_4326_LEVL_2.shp")

# paths to download climate data
pathTemp <- "https://envidatrepo.wsl.ch/uploads/chelsa/chelsa_V1/timeseries/tmean/CHELSA_tmean_"
pathPrec <- "https://envidatrepo.wsl.ch/uploads/chelsa/chelsa_V1/timeseries/prec/CHELSA_prec_"

# @prov.description stackClimate downloads all monthly climate files of a year, aggregates them by factor 10 and stacks them
stackClimate <- function(path,year){
  stack(
    lapply(formatC(1:2,flag=0,width=2),function(m){
      rasterClimate <- raster(paste0(path,year,"_",m,"_V1.2.1.tif"))
      NAvalue(rasterClimate) <- 65535
      raster::aggregate(rasterClimate,10)
    })
  )
}

# @prov.description maskClimateYear only keep climate values within cells with croplands and if it is within growing period, then calculate annual mean  
maskClimateYear <- function(stackClimate,stackCropland,stackCrop){
  stackCropClimate <- stackClimate*stackCropland*stackCrop
  calc(stackCropClimate, fun = mean,na.rm=T)
}

## iterate through target years
# @prov.unit lsClimateCrops = lapply(dfFinal) basalChange
lsClimateCrops <- lapply(1979:2008,function(y){
  
  # get cropland year that is closest to actual year
  croplandYear <- which(abs(seq(1980,2010,10)-y)==min(abs(seq(1980,2010,10)-y)))
  
  ## prepare climate data
  # @prov.unit stackTemp = stackClimate(pathTemp) valueChange
  stackTemp <- stackClimate(pathTemp,y)
  removeTmpFiles()
  
  stackPrec <- stackClimate(pathTemp,y)
  removeTmpFiles()
  
  ## extract climate for crops
  # @prov.unit meanMaizeTemp = maskClimateYear(stackTemp,stackCroplandBinary[[croplandYear]],stackMaize) basalChange
  meanMaizeTemp <- maskClimateYear(stackTemp,stackCroplandBinary[[croplandYear]],stackMaize)
  # @prov.unit meanMaizePrec = maskClimateYear(stackPrec,stackCroplandBinary[[croplandYear]],stackMaize) basalChange
  meanMaizePrec <- maskClimateYear(stackPrec,stackCroplandBinary[[croplandYear]],stackMaize)

  # @prov.unit meanWheatTemp = maskClimateYear(stackTemp,stackCroplandBinary[[croplandYear]],stackWheat) basalChange
  meanWheatTemp <- maskClimateYear(stackTemp,stackCroplandBinary[[croplandYear]],stackWheat)
  # @prov.unit meanWheatPrec = maskClimateYear(stackPrec,stackCroplandBinary[[croplandYear]],stackWheat) basalChange
  meanWheatPrec <- maskClimateYear(stackPrec,stackCroplandBinary[[croplandYear]],stackWheat)
  
  # @prov.unit meanRiceTemp = maskClimateYear(stackTemp,stackCroplandBinary[[croplandYear]],stackRice) basalChange
  meanRiceTemp <- maskClimateYear(stackTemp,stackCroplandBinary[[croplandYear]],stackRice)
  # @prov.unit meanRicePrec = maskClimateYear(stackPrec,stackCroplandBinary[[croplandYear]],stackRice) basalChange
  meanRicePrec <- maskClimateYear(stackPrec,stackCroplandBinary[[croplandYear]],stackRice)
  
  # @prov.unit meanSoybeansTemp = maskClimateYear(stackTemp,stackCroplandBinary[[croplandYear]],stackSoybeans) basalChange
  meanSoybeansTemp <- maskClimateYear(stackTemp,stackCroplandBinary[[croplandYear]],stackSoybeans)
  # @prov.unit meanSoybeansPrec = maskClimateYear(stackPrec,stackCroplandBinary[[croplandYear]],stackSoybeans) basalChange
  meanSoybeansPrec <- maskClimateYear(stackPrec,stackCroplandBinary[[croplandYear]],stackSoybeans)
  
  ## extract information to data frame (by political units)
  # @prov.unit stackCropTemp = stack(meanMaizeTemp,meanWheatTemp,meanRiceTemp,meanSoybeansTemp) basalChange
  stackCropTemp <- stack(list(meanMaizeTemp,meanWheatTemp,meanRiceTemp,meanSoybeansTemp))
  # @prov.description extract extracts weighted mean values from raster to shapefile
  # @prov.unit dfTemp = extract(stackCropTemp,NUTS2_shape) valueChange
  dfTemp <- raster::extract(stackCropTemp,NUTS2_shape,fun=mean,na.rm=TRUE,weights=TRUE,normalizeWeights=TRUE,sp=TRUE)
  dfTemp <- as.data.frame(dfTemp[c("NUTS_ID","layer.1","layer.2","layer.3","layer.4")])
  names(dfTemp)[2:5] <- c("maize","wheat","rice","soybeans")
  dfTemp <- dfTemp %>% gather(crop, temperature, "maize":"soybeans")

  # @prov.unit stackCropPrec = stack(meanMaizePrec,meanWheatPrec,meanRicePrec,meanSoybeansPrec) basalChange
  stackCropPrec <- stack(list(meanMaizePrec,meanWheatPrec,meanRicePrec,meanSoybeansPrec))
  # @prov.unit dfPrec = extract(stackCropPrec,NUTS2_shape) valueChange
  dfPrec <- raster::extract(stackCropPrec,NUTS2_shape,fun=mean,na.rm=TRUE,weights=TRUE,normalizeWeights=TRUE,sp=TRUE)
  dfPrec <- as.data.frame(dfPrec[c("NUTS_ID","layer.1","layer.2","layer.3","layer.4")])
  names(dfPrec)[2:5] <- c("maize","wheat","rice","soybeans")
  dfPrec <- dfPrec %>% gather(crop, precipitation, "maize":"soybeans")
  
  # @prov.unit dfFinal = merge(dfTemp,dfPrec) basalChange
  dfFinal <- merge(dfTemp,dfPrec, by=c("NUTS_ID","crop"))
  dfFinal$year <- y
  dfFinal[,c("NUTS_ID","year","crop","temperature","precipitation")]
})
# @prov.unit dfClimateCrops = rbind(lsClimateCrops) basalChange
dfClimateCrops <- do.call(rbind, lsClimateCropsYear)

# @prov.unit dfClimateCrops = convertCelsius(dfClimateCrops) unitChange 

# same input and output: problem?
dfClimateCrops$temperature <- dfClimateCrops$temperature/10 - 273.15
# @prov.unit dfClimateCrops = round(dfClimateCrops) valueChange
dfClimateCrops$temperature <- round(dfClimateCrops$temperature,0)
dfClimateCrops$precipitation <- round(dfClimateCrops$precipitation,0)


#### read growing data
dfHarvestedArea <- read.csv("cropAreas.csv")
dfHarvestedAreaTot <- aggregate(harvestedArea~NUTS_ID+year,dfHarvestedArea,sum) # tot harvested area per year and unit
names(dfHarvestedAreaTot)[3] <- "harvestedAreaTot"

# @prov.unit dfClimateAreaCrops = merge(dfClimateCrops,dfHarvestedArea) basalChange 
dfClimateAreaCrops <- merge(dfClimateCrops,dfHarvestedArea,by=c("NUTS_ID","year","crop"))
dfClimateAreaCrops <- merge(dfClimateAreaCrops,dfHarvestedAreaTot,by=c("NUTS_ID","year"))

#### read climate response data
setwd("C:/Users/egli/Nextcloud/Cloud/GeoKur/UseCases/1/Data/climateResponse")
dfTemperature <- read.csv("dfSuitabilityTemperature.csv")
dfTemperature <- dfTemperature[,c("climate","maize","wheat","rice","soy")]
names(dfTemperature)[c(1,5)] <- c("temperature","soybeans")
dfTemperature <- dfTemperature %>% gather(crop, suitabilityTemp, "maize":"soybeans")

dfPrecipitation <- read.csv("dfSuitabilityPrecipitation.csv")
dfPrecipitation <- dfPrecipitation[,c("climate","maize","wheat","rice","soy")]
names(dfPrecipitation)[c(1,5)] <- c("precipitation","soybeans")
dfPrecipitation <- dfPrecipitation %>% gather(crop, suitabilityPrec, "maize":"soybeans")

## merge
# @prov.unit dfClimateAreaResponseCrops = merge(dfClimateAreaCrops,dfTemperature,dfPrecipitation) basalChange 
dfClimateAreaResponseCrops <- merge(dfClimateAreaCrops,dfTemperature,by=c("crop","temperature"))
dfClimateAreaResponseCrops <- merge(dfClimateAreaResponseCrops,dfPrecipitation,by=c("crop","precipitation"))


#### calculate mean suitability
# @prov.description modelSuitability calculate suitability for given climate weighted by relative area harvested
modelSuitability <- function(dfInput){
  dfInput$suitability <- apply(dfInput[,c("suitabilityTemp","suitabilityPrec")],1,min)
  dfInput$meanSuitability <- dfInput$suitability*(dfInput$harvestedArea/dfInput$harvestedAreaTot)
  aggregate(meanSuitability~NUTS_ID+year,dfInput,sum)
}
# @prov.unit dfSuitabilityYear = modelSuitability(ClimateCropsGeoYear) coreConcept
dfSuitabilityYear <- modelSuitability(dfClimateAreaResponseCrops)


## add time intervals
dfSuitabilityYear$timeInterval <- NA
dfSuitabilityYear[which(dfSuitabilityYear$year%in%1979:1988),"timeInterval"] <- 1979
dfSuitabilityYear[which(dfSuitabilityYear$year%in%1989:1998),"timeInterval"] <- 1989
dfSuitabilityYear[which(dfSuitabilityYear$year%in%1999:2008),"timeInterval"] <- 1999
dfSuitabilityYear <- na.omit(dfSuitabilityYear)

## caclulate cv for each time interval
# @prov.description aggregate calculates the coefficient of variance for mean suitability for each time interval and political unit
# @prov.unit dfVariability = aggregate(dfSuitabilityYear) semanticShift
dfVariability <- aggregate(meanSuitability~NUTS_ID+timeInterval,dfSuitabilityYear,function(i){sd(i)/mean(i)})


rm(list=ls())
