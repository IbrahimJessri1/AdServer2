
from pymongo import MongoClient
from repositries import generics as gen


conn = MongoClient("mongodb://localhost:27017/AdServer")


advertisement_collection = conn.AdServer2.advertisement
interactive_advertisement_collection = conn.AdServer2.interactive_advertisement
user_collection = conn.AdServer2.user
role_permission_collection = conn.AdServer2.role_permission

served_ad_collection = conn.AdServer2.served_ad


