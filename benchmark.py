import time
import os
os.environ['PELIT_FOLDER'] = '.'
os.environ['PROSENTIT_FOLDER'] = '.'

from Kelly.veikkaus import listat

start = time.time()
for _ in range(5):
    listat()
end = time.time()
print(f"Time taken without cache: {end - start:.4f} seconds")
