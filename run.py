# run.py
import uvicorn
from dotenv import load_dotenv
import os
from app.core.config import settings

# 加载.env文件中的环境变量
load_dotenv()

# 验证环境变量是否加载成功
print("API_KEY loaded:", os.getenv("DASHSCOPE_API_KEY") is not None)
print("BASE_URL loaded:", os.getenv("DASHSCOPE_BASE_URL") is not None)
print("DATABASE_URL:", settings.database_url)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

