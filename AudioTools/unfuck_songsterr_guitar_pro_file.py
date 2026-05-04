import os
import guitarpro
from pathlib import Path
import copy

def clonar_trilha_limpa(track_original, song_nova):
    """
    Cria uma nova trilha na song_nova e copia apenas os dados musicais
    da track_original, ignorando metadados visuais.
    """
    # Cria uma trilha nova vinculada à nova música
    nova_track = guitarpro.Track(song_nova)
    
    # 1. Copia propriedades básicas
    nova_track.name = track_original.name
    nova_track.color = track_original.color
    nova_track.isPercussionTrack = track_original.isPercussionTrack
    
    # 2. Copia a configuração do instrumento (MIDI)
    nova_track.channel.instrument = track_original.channel.instrument
    nova_track.channel.volume = track_original.channel.volume
    nova_track.channel.balance = track_original.channel.balance
    nova_track.channel.chorus = track_original.channel.chorus
    nova_track.channel.reverb = track_original.channel.reverb
    
    # 3. Copia a Afinação (Número de cordas e notas)
    # Isso é crucial para o tablatura bater certo
    nova_track.strings = copy.deepcopy(track_original.strings)
    
    # 4. O Pulo do Gato: Copiar os compassos (Notas)
    # Mas forçar a limpeza de letras e diagramas dentro deles se houver
    nova_track.measures = copy.deepcopy(track_original.measures)
    
    # 5. SANITIZAÇÃO: Garante que não sobrou lixo
    nova_track.lyrics = guitarpro.Lyrics() # Mata letras
    # (Diagramas geralmente ficam na lista de acordes da música, não só na track, 
    # mas ao criar uma Song nova, a lista de acordes global já nasce vazia).
    
    return nova_track

def reconstruir_arquivo():
    caminho_input = input("Mestre, onde está o arquivo ou pasta? ").strip()
    caminho_input = caminho_input.replace('"', '').replace("'", "")
    path_origem = Path(caminho_input)
    
    # Detecta se é arquivo ou pasta
    if path_origem.is_file():
        arquivos = [path_origem]
        pasta_base = path_origem.parent
    else:
        arquivos = list(path_origem.glob("*.gp*"))
        pasta_base = path_origem

    pasta_render = pasta_base / "render"
    if not pasta_render.exists():
        pasta_render.mkdir()

    for arquivo in arquivos:
        if "render" in str(arquivo.parent): continue
        
        print(f"Reconstruindo: {arquivo.name}...")
        
        try:
            # Lê o original (sujo)
            song_velha = guitarpro.parse(str(arquivo))
            
            # --- CRIA A MÚSICA NOVA (VIRGEM) ---
            song_nova = guitarpro.Song()
            song_nova.title = song_velha.title
            song_nova.artist = song_velha.artist
            song_nova.tempo = song_velha.tempo
            
            # Remove a trilha padrão que vem na Song nova
            song_nova.tracks = []

            # Transplanta cada trilha
            for track_velha in song_velha.tracks:
                track_nova = clonar_trilha_limpa(track_velha, song_nova)
                song_nova.tracks.append(track_nova)

            # Salva
            nome_saida = arquivo.stem + "_clean.gp5"
            caminho_saida = pasta_render / nome_saida
            
            guitarpro.write(song_nova, str(caminho_saida))
            print(f"✅ Arquivo recriado do zero: {nome_saida}")

        except Exception as e:
            print(f"❌ Erro ao ler {arquivo.name}: {e}")
            if "unsupported version" in str(e):
                print("   (Dica: Use aquele .gp5 que você salvou manualmente como entrada)")

    print("\nOperação concluída, Mestre.")

if __name__ == "__main__":
    reconstruir_arquivo()