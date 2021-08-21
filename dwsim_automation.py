import pythoncom
pythoncom.CoInitialize()

import clr

from os import system as System
from System.IO import Directory, Path, File
from System import String, Environment

dwsimpath = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM6\\"

clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")

clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations
from DWSIM.Automation import Automation2
from DWSIM.GlobalSettings import Settings

Directory.SetCurrentDirectory(dwsimpath)

# create automation manager

interf = Automation2()

sim = interf.CreateFlowsheet()

# add water

water = sim.AvailableCompounds["Water"]

sim.SelectedCompounds.Add(water.Name, water)

# create and connect objects

m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "heat")
h1 = sim.AddObject(ObjectType.Heater, 100, 50, "heater")

sim.ConnectObjects(m1.GraphicObject, h1.GraphicObject, -1, -1)
sim.ConnectObjects(h1.GraphicObject, m2.GraphicObject, -1, -1)
sim.ConnectObjects(e1.GraphicObject, h1.GraphicObject, -1, -1)

sim.AutoLayout()

# steam tables property package

stables = PropertyPackages.SteamTablesPropertyPackage()

sim.AddPropertyPackage(stables)

# set inlet stream temperature
# default properties: T = 298.15 K, P = 101325 Pa, Mass Flow = 1 kg/s

m1.SetTemperature(300) # K
m1.SetMassFlow(100) # kg/s

# set heater outlet temperature

h1.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature
h1.OutletTemperature = 400 # K

# request a calculation

Settings.SolverMode = 0

errors = interf.CalculateFlowsheet2(sim)

print(String.Format("Heater Heat Load: {0} kW", h1.DeltaQ))

# save file

#path2save = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "/DWSIM_automation2")
path2save = Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + "/DWSIM_automation_python"
from os import makedirs
makedirs(path2save, exist_ok=True)

#fileNameToSave = Path.Combine(path2save, "/heatersample.dwxmz")
fileNameToSave = path2save + "/heatersample.dwxmz"

interf.SaveFlowsheet(sim, fileNameToSave, True)

# save the pfd to an image and display it

clr.AddReference(dwsimpath + "SkiaSharp.dll")
clr.AddReference("System.Drawing")

from SkiaSharp import SKBitmap, SKImage, SKCanvas, SKEncodedImageFormat
from System.IO import MemoryStream
from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat

PFDSurface = sim.GetSurface()

bmp = SKBitmap(1024, 768)
canvas = SKCanvas(bmp)
canvas.Scale(1.0)
PFDSurface.UpdateCanvas(canvas)
d = SKImage.FromBitmap(bmp).Encode(SKEncodedImageFormat.Png, 100)
str = MemoryStream()
d.SaveTo(str)
image = Image.FromStream(str)
#imgPath = Path.Combine(path2save, "/pfd.png")
imgPath = path2save + "/pfd.png"
image.Save(imgPath, ImageFormat.Png)
str.Dispose()
canvas.Dispose()
bmp.Dispose()

from PIL import Image

im = Image.open(imgPath)
im.show()