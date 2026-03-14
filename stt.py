from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

inference_pipeline = pipeline(
    task=Tasks.auto_speech_recognition,
    model='iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
    model_revision="v2.0.4")

rec_result = inference_pipeline('./bilibili_video/BV1g8PfzkELG/【3月10日午】特朗普：对伊朗军事行动很快结束；伊朗摧毁以色列关键卫星中心，宣布打击美军乌代里直升机基地；俄罗斯文化大楼被以军摧毁；马克龙登上戴高乐航母.wav')
print(rec_result)