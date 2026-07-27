import numpy as np

# Reproduce the weight math with actual val MAEs from the run
mae_lr = 64.27
mae_rf = 38.09
mae_gb = 29.54

inv_lr = 1.0 / mae_lr
inv_rf = 1.0 / mae_rf
inv_gb = 1.0 / mae_gb
total  = inv_lr + inv_rf + inv_gb

w_lr = inv_lr / total
w_rf = inv_rf / total
w_gb = inv_gb / total

print(f"inv_lr={inv_lr:.6f}, inv_rf={inv_rf:.6f}, inv_gb={inv_gb:.6f}")
print(f"total={total:.6f}")
print(f"w_lr={w_lr:.6f} ({w_lr*100:.1f}%)")
print(f"w_rf={w_rf:.6f} ({w_rf*100:.1f}%)")
print(f"w_gb={w_gb:.6f} ({w_gb*100:.1f}%)")
print(f"SUM = {w_lr+w_rf+w_gb:.6f}")
