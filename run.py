import uvicorn
from config.settings import settings

if __name__ == "__main__":
    print("=" * 50)
    print("🎓 EduAgent — AI Learning Assistant")
    print("=" * 50)
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
