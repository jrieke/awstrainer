import time
import pathlib
from datetime import datetime

print("Starting the mockup training script...")

# Write some dummy output to timestamped folder.
out_dir = pathlib.Path(f"out/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
out_dir.mkdir(parents=True, exist_ok=True)
with open(out_dir / "results.txt", "w+") as f:
    f.write("Dummy results")
print("Wrote results to:", out_dir)

time.sleep(2)
print("Training has finished!")
