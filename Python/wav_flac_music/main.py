import os
import time
from pydub import AudioSegment
import eyed3
from mutagen.flac import FLAC
from concurrent.futures import ThreadPoolExecutor

def safe_remove(file_path, max_retries=3):
    """安全删除文件，带有重试机制"""
    for i in range(max_retries):
        try:
            os.remove(file_path)
            return True
        except PermissionError:
            time.sleep(0.1 * (i+1))
    return False

def convert_sample_width(audio):
    """处理非常规sample width"""
    try:
        if audio.sample_width not in [1, 2, 3, 4]:
            return audio.set_sample_width(2)
        return audio
    except Exception as e:
        print(f"采样位数修复失败: {str(e)}")
        return None

def convert_and_clean(wav_path):
    flac_path = None
    try:
        audio = AudioSegment.from_file(wav_path, format='wav')
        audio = convert_sample_width(audio)
        if audio is None:
            raise ValueError("不支持的音频格式")

        tags = {}
        try:
            audiofile = eyed3.load(wav_path)
            if audiofile and audiofile.tag:
                tags = {
                    'ARTIST': audiofile.tag.artist or '',
                    'ALBUM': audiofile.tag.album or '',
                    'TITLE': audiofile.tag.title or '',
                    'GENRE': audiofile.tag.genre.name if audiofile.tag.genre else '',
                    'DATE': str(audiofile.tag.getBestDate()) or '',
                    'TRACKNUMBER': str(audiofile.tag.track_num[0]) if audiofile.tag.track_num else ''
                }
        except Exception as e:
            print(f"元数据读取警告: {str(e)}")

        flac_path = os.path.splitext(wav_path)[0] + '.flac'
        
        with open(flac_path, 'wb') as f:
            audio.export(f, format='flac')

        if tags:
            flac_audio = FLAC(flac_path)
            flac_audio.delete()
            flac_audio.update(tags)
            flac_audio.save()

        if os.path.exists(flac_path) and os.path.getsize(flac_path) > 0:
            if safe_remove(wav_path):
                print(f"成功转换并删除: {wav_path}")
                return True
        return False

    except Exception as e:
        print(f"处理失败 {wav_path}: {str(e)}")
        if flac_path and os.path.exists(flac_path):
            safe_remove(flac_path)
        return False

def batch_convert():
    deleted_count = 0
    error_count = 0
    
    # 自动根据CPU核心数设置线程数（核心数*2）
    max_workers = os.cpu_count() * 2 or 4
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for root, _, files in os.walk('.'):
            for file in files:
                if file.lower().endswith('.wav'):
                    full_path = os.path.join(root, file)
                    futures.append(executor.submit(convert_and_clean, full_path))

        for future in futures:
            try:
                if future.result():
                    deleted_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"线程执行出错: {str(e)}")
                error_count += 1

    print(f"\n转换总结：\n成功转换并删除: {deleted_count} 个文件\n失败文件: {error_count} 个")

if __name__ == "__main__":
    print("=== WAV转FLAC工具 (增强安全版) ===")
    print(f"当前CPU核心数: {os.cpu_count()}")
    print("开始批量转换...\n")
    batch_convert()
    input("\n按任意键退出...")