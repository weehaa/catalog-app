from sqlalchemy import create_engine
from sqlalchemy import asc, desc, func
from database_setup import User, Category, Item, Base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# User CRUD methods
def user_count():
    return session.query(User).count()

def user_byid(id):
    return session.query(User).filter_by(id=id).one()

def user_byname(name):
    return session.query(User).filter_by(name=name).one()

def user_byemail(email):
    try:
        return session.query(User).filter_by(email=email).one()
    except:
        return None

def user_add(name, email, picture=None):
    newUser = User(name=name, email=email, picture=picture)
    session.add(newUser)
    session.commit()
    return user_byemail(email)

def user_update(user, name=None, email=None, picture=None):
    if name:
        user.name = name
    if email:
        user.email = email
    if picture:
        user.picture = picture
    session.add(user)
    session.commit()
    return

def delete_user(user):
    session.delete(user)
    session.commit()
    return

# Category CRUD methods
def category_count():
    return session.query(Category).count()

def category_all():
    return session.query(Category).all()

def category_byid(id):
    return session.query(Category).filter_by(id=id).one()

def category_byname(name):
    return session.query(Category).filter_by(name=name).one()

def category_add(name):
    newCategory = Category(name=name)
    session.add(newCategory)
    session.commit()
    return

def category_update(category, name):
    category.name = name
    session.add(category)
    session.commit()
    return

def delete_category(category):
    session.delete(category)
    session.commit()
    return

# Item CRUD methods
def items_count():
    return session.query(Item).count()

def items_latest():
    """@return a tuple of Item and Category objects"""
    return session.query(Item, Category).join(Category).\
           order_by(desc(Item.id)).all()

def items_bycat(category_name):
    category_id = category_byname(category_name).id
    return session.query(Item).\
           filter(Item.category_id == category_id).\
           order_by(desc(Item.id)).all()

def item_byid(id):
    return session.query(Item).filter_by(id=id).one()

def item_byCatAndName(category_name, item_name):
    return session.query(Item).join(Category).\
           filter(Item.name == item_name).\
           filter(Category.name == category_name).one()

def item_add(name, category_name, user_id, description=None):
    try:
        category_id = category_byname(category_name).id
        newItem = Item(name=name, user_id=user_id,
                       description=description,
                       category_id=category_id)
        session.add(newItem)
        session.commit()
        return item_byCatAndName(category_name, name)
    except:
        return None

def item_update(item, name, description):
    item.name = name
    session.add(item)
    session.commit()
    return

def delete_item(item):
    session.delete(item)
    session.commit()
    return
