import os
from sentence_transformers import SentenceTransformer
from huggingface_hub import hf_hub_download

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:50075'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:50075'

model_name = 'shibing624/text2vec-base-chinese'


print("正在下载模型到本地缓存...")
model = SentenceTransformer(model_name)
print("模型下载完成，本地缓存路径:", model_name)
