from uuid import uuid4
from fastapi import HTTPException, status
from config.db import advertisement_collection, interactive_advertisement_collection, served_ad_collection
from models.ads_stats import ServedAd
from repositries import generics as gen
from models.advertisement import AdInfo, Advertisement, AdvertisementShow, InteractiveAdvertisementInput, MarketingInfo, InteractiveAdvertisement, InteractiveMarketingInfo, AdType, InteractiveAdvertisementShow
import datetime
from .utilites import get_dict, limited_get, download_file


def create_ad(ad_input, advertiser_username, interactive = 0):
    try:
        create_date = str(datetime.datetime.now())
        ad_info = AdInfo(type = ad_input.type, advertiser_username=advertiser_username, text=ad_input.text,  width=ad_input.width, height=ad_input.height, shape=ad_input.shape)
        id = str(uuid4())
        if interactive:
            advertisement = InteractiveAdvertisement(
                id= id,
                create_date = create_date,
                target_user_info=ad_input.target_user_info, 
                marketing_info=InteractiveMarketingInfo(max_cpc= ad_input.max_cpc,impressions= 0, clicks=0, raise_percentage=ad_input.raise_percentage),
                ad_info= ad_info,
                categories=ad_input.categories,
                url= ad_input.url,
                redirect_url=ad_input.redirect_url,
                keywords=ad_input.keywords
            )
            collection = interactive_advertisement_collection
        else:
            advertisement = Advertisement(
                id= id,
                create_date = create_date,
                target_user_info=ad_input.target_user_info, 
                marketing_info=MarketingInfo(max_cpc= ad_input.max_cpc,impressions= 0, raise_percentage=ad_input.raise_percentage),
                ad_info= ad_info,
                categories=ad_input.categories,
                url= ad_input.url,
                keywords=ad_input.keywords
            )
            collection = advertisement_collection
        ad = get_dict(advertisement)
        collection.insert_one(dict(ad))
        return id
    except:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error happened, try again later')


def get_my_ads(username, limit, skip, interactive, type, shape):
    constraints = {"ad_info.advertiser_username" : username}
    if type != 'all':
        constraints = {"$and" : [constraints, {"ad_info.type" : type}]}
    if shape != 'all':
        constraints = {"$and" : [constraints, {"ad_info.shape" : shape}]}
    if interactive == 2:
        res1 = limited_get(collection=interactive_advertisement_collection, limit=limit, skip=skip, constraints= constraints)
        res2 = limited_get(collection=advertisement_collection, limit=limit, skip=skip, constraints= constraints)
        ads = []
        for ad in res1:
            ads.append(toAdShow(ad, 1))
        for ad in res2:
            ads.append(toAdShow(ad, 0))
        return ads
    else:
        collection = advertisement_collection
        if interactive == 1:
            collection = interactive_advertisement_collection
        res =  limited_get(collection=collection, limit=limit, skip=skip, constraints= constraints)
        ads = []
        for ad in res:
            ads.append(toAdShow(ad, interactive))
        return ads


def get_my_served_ads(username, limit, skip):
    res =  limited_get(collection=served_ad_collection, limit=limit, skip=skip, constraints= {"advertiser_username" : username})
    ads = []
    for ad in res:
        ads.append(toServedAd(ad))
    return ads



##admin uses
def get(constraints, limit, skip, interactive):
    collection = advertisement_collection
    if interactive:
        collection = interactive_advertisement_collection
    return limited_get(collection=collection, limit=limit, skip=skip, constraints= constraints)


def remove(constraints):
    gen.remove(advertisement_collection, constraints)
    


def get_ad(id, username):
    query = {"$and" : [{"ad_info.advertiser_username" : username}, {"id" : id}]}
    ad = gen.get_one(advertisement_collection, query)
    if ad:
        return toAdShow(ad)
    ad = gen.get_one(interactive_advertisement_collection, {"$and" : [{"ad_info.advertiser_username" : username}, {"id" : id}]})
    if ad:
        return toAdShow(ad, 1)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no such id")


def get_served_ad(id, username):
    query = {"$and" : [{"advertiser_username" : username}, {"id" : id}]}
    ad = gen.get_one(served_ad_collection, query)
    if ad:
        return toServedAd(ad)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no such id")


def toAdShow(ad, interactive = 0):
    if interactive:
        return  InteractiveAdvertisementShow(
                    id= ad["id"],
                    create_date=ad["create_date"],
                    target_user_info=ad["target_user_info"],
                    marketing_info=ad["marketing_info"],
                    ad_info=ad["ad_info"], 
                    categories=ad["categories"],
                    keywords=ad["keywords"],
                    url = ad["url"],
                    redirect_url=ad["redirect_url"]
                )
    # try:
    return  AdvertisementShow(
                    id= ad["id"],
                    create_date=ad["create_date"],
                    target_user_info=ad["target_user_info"],
                    marketing_info=ad["marketing_info"],
                    ad_info=ad["ad_info"], 
                    categories=ad["categories"],
                    keywords=ad["keywords"],
                    url = ad["url"]
            )
    # except Exception as e:
    #     raise e


def toServedAd(served_ad):
    return ServedAd(
        id= served_ad["id"],
        agreed_cpc=served_ad["agreed_cpc"], 
        ad_id=served_ad["ad_id"], 
        impressions=served_ad["impressions"], 
        clicks=served_ad["clicks"],
        advertiser_username=served_ad["advertiser_username"]
        )


def get_tot_payment(username):
    tot = 0
    res = gen.get_many(served_ad_collection, {"advertiser_username" : username})
    for item in res:
        tot += int(item["clicks"]) * float(item["agreed_cpc"])
    return {"total" : tot}


def get_ad_payment(username, ad_id):
    tot = 0
    res = gen.get_many(served_ad_collection, {"$and" : [{"advertiser_username" : username}, {"ad_id" : ad_id}]})
    for item in res:
        tot += int(item["clicks"]) * float(item["agreed_cpc"])
    return {"total" : tot}