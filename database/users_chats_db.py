import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT
from datetime import datetime, timedelta

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        
        
    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            Premium=False, # user is premium or not
            premium_expiry=None, # duration of premium
            purchase_date=None, # date of purchase
            timestamps=0, # floodwait time
            user_joined=False, # user joined or not
            files_count=0, # Daily files count
            lifetime_files=0, # Lifetime files count
            last_reset=datetime.now().strftime("%Y-%m-%d"), # Last reset date
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )
    
    #get user from database
    async def get_user(self, id):
        user = await self.col.find_one({'id': int(id)})
        return False if not user else user
    
    # update files count of user
    async def update_files_count(self, user_id, count):
        await self.col.update_one(
        {"id": user_id}, 
        {"$set": {"files_count": count}}
    )

    # get files count of user
    async def get_files_count(self, user_id):
        user = await self.col.find_one({"id": user_id})
        return user.get("files_count", 0)
    
    # update total files count of user
    async def update_lifetime_files(self, user_id, count):
        await self.col.update_one(
        {"id": user_id}, 
        {"$set": {"lifetime_files": count}}
    )

    # get total files count of user
    async def get_lifetime_files(self, user_id):
        user = await self.col.find_one({"id": user_id})
        return user.get("lifetime_files", 0)


    # check last reset date of user
    async def get_last_reset(self, user_id):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            return None
        return user.get("last_reset")
    
    # reset fiiles count of user
    async def reset_daily_files_count(self, user_id):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            return
        await self.col.update_one({"id": user_id}, {"$set": {"files_count": 0, "last_reset": datetime.now().strftime("%Y-%m-%d")}})

    # reset files count for all user forcefully
    async def reset_all_files_count(self):
        await self.col.update_many({}, {"$set": {"files_count": 0}})

    async def get_timestamps(self, id):
        user = await self.col.find_one({"id": id})
        if user is None:
            return None
        return user.get("timestamps")

    async def update_timestamps(self, id, time):
        await self.col.update_one({"id": id}, {"$set": {"timestamps": time}})

    async def is_user_joined(self, id):
        user = await self.col.find_one({"id": id})
        if user is None:
            return False
        return user.get("user_joined")

    async def update_user_joined(self, id, status):
        await self.col.update_one({"id": id}, {"$set": {"user_joined": status}}) 

    async def reset_all_users_joined(self):
        await self.col.update_many({}, {"$set": {"user_joined": False}})

    async def is_premium_status(self, user_id):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            return False  # User not found in the database
        return user.get("Premium", False)

    # add user as premium
    async def add_user_as_premium(self, user_id, expiry_date, subscription_date):
        await self.col.update_one(
            {"id": user_id},
            {"$set": {"Premium": True, "premium_expiry": expiry_date, "purchase_date": subscription_date}}
        )

    # remove user from premium
    async def remove_user_premium(self, user_id):
        await self.col.update_one({"id": user_id}, {"$set": {"Premium": False, "premium_expiry": None, "purchase_date": None}})
         
    # check user is expired or not if expired then remove premium
    async def check_expired_users(self, user_id):
        user = await self.col.find_one({"id": user_id})
        now_timestamp = int(datetime.now().timestamp())  # Convert now to UNIX timestamp

        if user is None:
            return  # User not found in the database
        
        premium_expiry_days = user.get("premium_expiry")
        purchase_date = user.get("purchase_date")

        if premium_expiry_days is None:
            return  # User does not have a premium expiry duration
        
        # Calculate the expiry timestamp based on premium_expiry_days
        premium_expiry_timestamp = purchase_date + (premium_expiry_days * 24 * 60 * 60)
        
        if now_timestamp > premium_expiry_timestamp:
            await self.remove_user_premium(user_id)
            return "Your subscription has expired."

    # remove all expired user
    async def remove_expired_users(self):
        now = datetime.utcnow()
        expired_users = await self.col.find({}).to_list(None)
        
        for user in expired_users:
            user_id = user['id']
            purchase_date = user.get('purchase_date')
            premium_expiry_days = user.get('premium_expiry')
            
            if purchase_date is not None and premium_expiry_days is not None:
                expiry_date = purchase_date + timedelta(days=premium_expiry_days)
                
                if expiry_date <= now:
                    await self.remove_user_premium(user_id)

    def new_group(self, id, title):
        return dict(
            id=id,
            title=title,
            api=0,
            shortner=None,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )
         
    async def update_api_for_group(self, group_id, api):
        await self.grp.update_one({'id': int(group_id)}, {'$set': {'api': api}})
        
    async def remove_api_for_group(self, group_id):
        await self.grp.update_one({'id': group_id}, {'$set': {'api': 0}})

    async def get_api_from_chat(self, group_id):
        group = await self.grp.find_one({'id': int(group_id)})
        api = group.get('api', '')
        if not api or api == 0:
            return False
        return api

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)
   
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
    
    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id': int(chat)})
        return False if not chat else chat.get('chat_status')
    
    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
        )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'template': IMDB_TEMPLATE
        }
        chat = await self.grp.find_one({'id': int(id)})
        if chat:
            return chat.get('settings', default)
        return default
    
    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
        )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    
    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

db = Database(DATABASE_URI, DATABASE_NAME)
