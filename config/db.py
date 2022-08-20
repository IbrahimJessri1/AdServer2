
from pymongo import MongoClient
from repositries import generics as gen


conn = MongoClient("mongodb://localhost:27017/AdServer2")


advertisement_collection = conn.AdServer2.advertisement
interactive_advertisement_collection = conn.AdServer2.interactive_advertisement
user_collection = conn.AdServer2.user
role_permission_collection = conn.AdServer2.role_permission

served_ad_collection = conn.AdServer2.served_ad


#gen.update_many(collection, {}, {"$set" : {"marketing_info.times_served" : 0} })


#print(all_ads[0]["marketing_info"]["max_cpc"])

# advertisement_collection.delete_many({})
# interactive_advertisement_collection.delete_many({})
# served_ad_collection.delete_many({})

# advertisement_collection.delete_many({})
# interactive_advertisement_collection.delete_many({})
# served_ad_collection.delete_many({})