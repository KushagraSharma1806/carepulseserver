from motor.motor_asyncio import AsyncIOMotorClient

uri = "mongodb+srv://kushagrasharma1806:Kushagra@carepulse.59jpq40.mongodb.net/?retryWrites=true&w=majority&appName=Carepulse"
client = AsyncIOMotorClient(uri)
try:
    client.admin.command('ping')
    print("✅ MongoDB connection successful")
except Exception as e:
    print("❌ Error connecting:", e)
