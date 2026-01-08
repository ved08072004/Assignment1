from database import collection

def create_user(user: dict):
    return collection.insert_one(user)

def get_all_users():
    return list(collection.find({}, {"_id": 0}))

def get_user_by_name(name: str):
    return collection.find_one({"name": name}, {"_id": 0})

def update_user(name: str, update_data: dict):
    return collection.update_one(
        {"name": name},
        {"$set": update_data}
    )

def delete_user(name: str):
    return collection.delete_one({"name": name})
