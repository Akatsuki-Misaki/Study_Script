import os
from pydub import AudioSegment
import eyed3
from mutagen.flac import FLAC

def convert_and_clean(wav_path):
    try:
        # 增强版元数据读取
        tags = {}
        audiofile = eyed3.load(wav_path)
        
        # 处理无标签文件
        if audiofile is not None and audiofile.tag is not None:
            tags = {
                'ARTIST': audiofile.tag.artist or '',
                'ALBUM': audiofile.tag.album or '',
                'TITLE': audiofile.tag.title or '',
                'GENRE': audiofile.tag.genre.name if audiofile.tag.genre else '',
                'DATE': str(audiofile.tag.getBestDate()) or '',
                'TRACKNUMBER': str(audiofile.tag.track_num[0]) if audiofile.tag.track_num else ''
            }
        else:
            # 从文件名提取基础信息
            filename = os.path.basename(wav_path)
            base_info = os.path.splitext(filename)[0].split('-', 1)
            if len(base_info) > 1:
                tags['ARTIST'] = base_info[0].strip()
                tags['TITLE'] = base_info[1].strip()

        # 转换音频格式
        flac_path = os.path.splitext(wav_path)[0] + '.flac'
        AudioSegment.from_wav(wav_path).export(flac_path, format='flac')

        # 写入FLAC元数据
        if tags:
            flac_audio = FLAC(flac_path)
            flac_audio.delete()
            flac_audio.update(tags)
            flac_audio.save()

        # 安全删除验证
        if os.path.exists(flac_path) and os.path.getsize(flac_path) > 0:
            os.remove(wav_path)
            print(f"成功转换并删除: {wav_path}")
            return True
        return False

    except Exception as e:
        print(f"处理失败 {wav_path}: {str(e)}")
        if 'flac_path' in locals() and os.path.exists(flac_path):
            os.remove(flac_path)
        return False

def batch_convert():
    deleted_count = 0
    error_count = 0
    
    for root, _, files in os.walk('.'):
        for file in files:
            if file.lower().endswith('.wav'):
                full_path = os.path.join(root, file)
                if convert_and_clean(full_path):
                    deleted_count += 1
                else:
                    error_count += 1

    print(f"\n转换总结：\n成功转换并删除: {deleted_count} 个文件\n失败文件: {error_count} 个")

if __name__ == "__main__":
    print("=== WAV转FLAC工具 (增强安全版) ===")
    batch_convert()