import asyncio
async def main():
    print("Start")
    await asyncio.sleep(2)  # 等待 2 秒，不阻塞主线程
    print("End")

if __name__ == "__main__":
    asyncio.run(main())

