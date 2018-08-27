import simplekml
kml = simplekml.Kml()

# ground1 = kml.newgroundoverlay(name='Blue Marble - Jan')
# ground1.icon.href = 'http://mw1.google.com/mw-earth-vectordb/kml-samples/bmng12/files/BMNG-Jan.jpg'
# ground1.gxlatlonquad.coords = [(-180,-90),(180,-90),(180,90),(-180,90)]
# ground1.timespan.begin = "2004-01-01"
# ground1.timespan.end = "2004-01-31"

# ground2 = kml.newgroundoverlay(name='Blue Marble - Feb')
# ground2.icon.href = 'http://mw1.google.com/mw-earth-vectordb/kml-samples/bmng12/files/BMNG-Feb.jpg'
# ground2.gxlatlonquad.coords = [(-180,-90),(180,-90),(180,90),(-180,90)]
# ground2.timespan.begin = "2004-02-01"
# ground2.timespan.end = "2004-02-29"

# ground3 = kml.newgroundoverlay(name='Blue Marble - Mar')
# ground3.icon.href = 'http://mw1.google.com/mw-earth-vectordb/kml-samples/bmng12/files/BMNG-Mar.jpg'
# ground3.gxlatlonquad.coords = [(-180,-90),(180,-90),(180,90),(-180,90)]
# ground3.timespan.begin = "2004-03-01"
# ground3.timespan.end = "2004-03-31"

# ...and so on with the other months
ls = kml.newlinestring(name="test", coords=[(175, -37)])
ls.style.linestyle.color = simplekml.Color.red  # Red
ls.style.linestyle.width = 10  # 10 pixels
ls.timespan.begin = "2018-08-21"
ls.timespan.end = "2018-08-22"

ls1 = kml.newlinestring(name="test1", coords=[(175, -37), (175, -27)])
ls1.style.linestyle.color = simplekml.Color.red  # Red
ls1.style.linestyle.width = 10  # 10 pixels
ls1.timespan.begin = "2018-08-22"
ls1.timespan.end = "2018-08-23"

ls2 = kml.newlinestring(name="test2", coords=[
                        (175, -37), (175, -27), (175, -17)])
ls2.style.linestyle.color = simplekml.Color.red  # Red
ls2.style.linestyle.width = 10  # 10 pixels
ls2.timespan.begin = "2018-08-23"
ls2.timespan.end = "2018-08-24"

kml.save("test.kml")
