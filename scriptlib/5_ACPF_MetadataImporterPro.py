# ACPF_upd_metadata2018.py
# Metadata handling remains one of ESRI's biggest challenges. We all know it's necessary so
# why do they make it so hard? A large collection of data requires individual metadata files
# for each feature class, table, and raster. In this case, 18 different entities. I use a series
# of templates since the metadata only changes for some ususally in an annual basis. In
# this script, only the land use related data changes for 2016...the land use raster, the FB
# feature class, LU6, and CH tables.The raster data always challenges me. In the past, I 
# used a saved .xml file (saving it to the right format? jeez) but this year an actual raster
# in the metadata templates FGDB -- where I store the remainder fo the tempates. And...
# remember, you can't just run this in a bulk processing script from the DOS prompt...ohhNoo
# You MUST run it in the foreground from ArcMAP Only! so add a temporary tool and run it 
# from there...because ??? WTF.
#
# Oh, and BTW...you can't use a 'in_memory' scratch workspace because...well, it just doesn't 
# work...and the raster import metadata leaves all these xml transformation trash files behind,
# so if you do not explictly create a scratchworkspace and then delete it it iw fill up and the 
# process (already very slow) slows to a crawl because the scratch workspace fills up. JFC
# D. James 04/2017
#
# Flash forward to 06/2018...all the above still applies, except using MetadataImporter tool is 
# about a gazillion times faster. Why are there two -- Import Metadata and Metadata Importer?
# Jack only knows and he ain't telling!
#
# May 2019 - Use a new HUC12 processing feature class (procHUC12_v2019)-- fields are now HUC8, HUC12
#
# Jan 2022 - Modify for use in the CA data collection; add entry for CA Bridge
#
# Import system modules
import arcpy
from arcpy import env
from arcpy import metadata as md
import sys, string, os, time

env.overwriteOutput = True

# Set extensions & environments 
arcpy.CheckOutExtension("Spatial")


##------------------------------------------------------------------------------
##------------------------------------------------------------------------------

def updMetadata(FGDBList, metaTemp):

    # Select & go
    arcpy.AddMessage(" fgdb: %s" %(FileGDB))
    env.workspace = FileGDB
    inHUC = os.path.split(FileGDB)[1][4:16]
    
    ## Field Boundaries 
    arcpy.AddMessage(" ...boundaries")
    fcList = ['bnd','buf','FB','LU6_','CH_']
    #fcList = ['buf']
    
    for fc in fcList:
        src_template = md.Metadata(metaTemp + "\\%sMetaTemplate" % fc)
        tgt_item = md.Metadata('%s%s' %(fc, inHUC))
        #arcpy.AddMessage('src: %s, target: %s' %(src_template.title,tgt_item.title))
        tgt_item.copy(src_template)
        tgt_item.save()
        
    del [fcList, src_template, tgt_item]

    
    # Soils 
    arcpy.AddMessage(" ...soils")
    src_template = md.Metadata(metaTemp + "\\gSSURGOMetaTemplate")
    tgt_item = md.Metadata('gSSURGO')
    tgt_item.copy(src_template)
    tgt_item.save()
    
    slList = ['SurfHrz','SurfTex','SoilProfile']
    #slList = []
    
    for sl in slList:
        src_template = md.Metadata(metaTemp + "\\%sMetaTemplate" % sl)
        tgt_item = md.Metadata('%s%s' %(sl, inHUC))
        tgt_item.copy(src_template)
        tgt_item.save()
        
    del [slList, src_template, tgt_item]

    # Land Use
    arcpy.AddMessage(" ...CDL")
    
    luList = ["2016","2017","2018","2019","2020","2021","2022","2023"]
    #luList = []

    for lu in luList:
        src_template = md.Metadata(metaTemp + "\\wsCDL%sMetaTemplate" % lu)
        tgt_item = md.Metadata('wsCDL%s' %(lu))
        tgt_item.copy(src_template)
        tgt_item.save()
        
    del [lu, luList, src_template, tgt_item]
    #del [luList]
    

##------------------------------------------------------------------------------
##------------------------------------------------------------------------------

if __name__ == "__main__":
    
    inHUC = sys.argv[1]
    prjFolder = sys.argv[2]

    #acpfDir = r"D:\ACPFdevelop\ACPF_OTFly\processingDir"
    HUC12status = r"D:\ACPFdevelop\ACPF_OTFly\nationalACPF\ACPF2023_Basedata.gdb\US48_HUC12_2023"   
    metaTemp = r"D:\ACPFdevelop\ACPF_OTFly\nationalACPF\Metadata_templates_2023Pro.gdb"


    sws = r"D:\ArcGISDefaults\scratchACPF"
            

    for row in arcpy.da.SearchCursor(HUC12status, ["HUC8","HUC12"], ''' "HUC12" = '%s' ''' %(inHUC) ):
        HUC8 = str(row[0])

        ProcDir = prjFolder + "\\huc" + HUC8
        FileGDB = ProcDir + "\\acpf" + inHUC + ".gdb"

        arcpy.AddMessage("..." + FileGDB)

        env.workspace = FileGDB
        env.extent = "buf" + inHUC
            
        updMetadata(FileGDB, metaTemp)

        arcpy.management.Compact(FileGDB)                        

        env.scratchWorkspace = ""
        arcpy.Delete_management(os.path.join(sws, "mytemp"))
    
