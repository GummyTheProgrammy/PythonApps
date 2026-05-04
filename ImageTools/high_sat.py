import cv2
import numpy as np
import os
from pathlib import Path
from tqdm import tqdm

def apply_cinematic_grade(img):
    # 1. Normalização para float (0 a 1) para cálculos precisos
    img = img.astype(np.float32) / 255.0
    
    # 2. Criar Máscaras de Luminância (Sombras e Realces)
    # Calculamos o brilho de cada pixel
    luminance = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    luminance = cv2.merge([luminance, luminance, luminance])
    
    # Máscara para sombras (mais forte onde é escuro)
    shadow_mask = 1.0 - luminance
    # Máscara para realces (mais forte onde é claro)
    highlight_mask = luminance

    # 3. Aplicar Split Toning
    # Injetando Teal (B=1.0, G=0.8, R=0.0) nas sombras
    # Injetando Orange (B=0.0, G=0.5, R=1.0) nos realces
    img_shadows = img + (shadow_mask * [0.15, 0.10, 0.0]) # Teal suave
    img_highlights = img_shadows + (highlight_mask * [0.0, 0.05, 0.12]) # Orange suave
    
    # 4. Roll-off dos Brancos (Efeito Creme e Anti-estouro)
    # Usamos uma função de ganho que achata os realces
    img_graded = np.clip(img_highlights, 0, 1)
    img_graded = img_graded * 0.9 + 0.05 # Reduz o teto e levanta levemente o piso
    
    # 5. Ajuste Final de Saturação e Contraste
    # Convertendo para HSV para "clampar" a saturação
    hsv = cv2.cvtColor((img_graded * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.2, 0, 180) # Saturação +20% com limite
    
    final_img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return final_img

def main():
    print("--- Cinematic Batch Processor (Teal & Orange) ---")
    input_dir = input("Mestre, forneça a pasta de entrada (PNGs da IA): ")
    output_dir = Path(input_dir) / "cinematic_edition"
    output_dir.mkdir(exist_ok=True)
    
    files = [f for f in Path(input_dir).iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
    
    print(f"Processando {len(files)} imagens com estilo praiano sobrenatural...")
    
    for file_path in tqdm(files):
        img = cv2.imread(str(file_path))
        if img is None: continue
        
        # Aplica a mágica
        result = apply_cinematic_grade(img)
        
        # Salva o resultado
        cv2.imwrite(str(output_dir / f"cinematic_{file_path.stem}.png"), result)

if __name__ == "__main__":
    main()