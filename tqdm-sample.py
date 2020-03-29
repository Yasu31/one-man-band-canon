from time import sleep
from tqdm import tqdm 
barA = tqdm(total=100, dynamic_ncols=True, bar_format="{l_bar}{bar}")
barA.set_description("second")
barB = tqdm(total=100, dynamic_ncols=True, bar_format="{l_bar}{bar}")
barB.set_description("third ")
for i in range(100):
    sleep(0.05)
    barA.n = i
    barB.n = 99-i
    barA.refresh()
    barB.refresh()
barA.close()
barB.close()