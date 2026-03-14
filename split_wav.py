import ffmpeg
import os


def mp4_to_wav(mp4_path, wav_path=None, sample_rate=16000, channels=1):
    """
    从 MP4 文件中提取音频并保存为 WAV
    :param mp4_path: 输入 MP4 文件路径
    :param wav_path: 输出 WAV 文件路径（默认同目录，替换后缀为 .wav）
    :param sample_rate: 采样率（默认 16000，适配 STT 模型）
    :param channels: 声道数（默认 1 单声道，适配 STT 模型）
    :return: 输出 WAV 文件路径
    """
    # 校验输入文件
    if not os.path.exists(mp4_path):
        raise FileNotFoundError(f"MP4 文件不存在：{mp4_path}")

    # 默认输出路径
    if wav_path is None:
        wav_path = os.path.splitext(mp4_path)[0] + ".wav"

    try:
        # 核心：FFmpeg 提取音频并转码为 WAV
        (
            ffmpeg
            .input(mp4_path)  # 输入 MP4
            .output(
                wav_path,
                format='wav',  # 输出格式 WAV
                ar=sample_rate,  # 采样率
                ac=channels,  # 声道数
                sample_fmt='s16'  # 位深 16bit（STT 模型通用）
            )
            .overwrite_output()  # 覆盖已存在的文件
            .run(quiet=True)  # 静默执行，不打印日志
        )
        print(f"音频提取成功：{wav_path}")
        return wav_path

    except ffmpeg.Error as e:
        raise RuntimeError(f"提取失败：{e.stderr.decode('utf-8')}") from e


# 示例调用
if __name__ == "__main__":
    # 替换为你的 MP4 文件路径
    mp4_file = "./bilibili_video/BV1g8PfzkELG/【3月10日午】特朗普：对伊朗军事行动很快结束；伊朗摧毁以色列关键卫星中心，宣布打击美军乌代里直升机基地；俄罗斯文化大楼被以军摧毁；马克龙登上戴高乐航母.mp4"
    # 提取音频（输出 16k 单声道 WAV，适配 FunASR 等 STT 模型）
    mp4_to_wav(mp4_file)