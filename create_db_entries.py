import crud

# Create test users
crud.user_add(name="Test1", email="test1@example.com",
             picture='https://lh4.ggpht.com/wKrDLLmmxjfRG2-E-k5L5BUuHWpCOe4lWRF7oVs1Gzdn5e5yvr8fj-ORTlBF43U47yI=w300')

crud.user_add(name="Test2", email="test2@example.com",
             picture='https://lh4.ggpht.com/wKrDLLmmxjfRG2-E-k5L5BUuHWpCOe4lWRF7oVs1Gzdn5e5yvr8fj-ORTlBF43U47yI=w300')

crud.user_add(name="Test3", email="test3@example.com",
             picture='https://lh4.ggpht.com/wKrDLLmmxjfRG2-E-k5L5BUuHWpCOe4lWRF7oVs1Gzdn5e5yvr8fj-ORTlBF43U47yI=w300')

crud.user_add(name="Test4", email="test4@example.com",
             picture='https://lh4.ggpht.com/wKrDLLmmxjfRG2-E-k5L5BUuHWpCOe4lWRF7oVs1Gzdn5e5yvr8fj-ORTlBF43U47yI=w300')

crud.user_add(name="Test5", email="test5@example.com",
             picture='https://lh4.ggpht.com/wKrDLLmmxjfRG2-E-k5L5BUuHWpCOe4lWRF7oVs1Gzdn5e5yvr8fj-ORTlBF43U47yI=w300')

# Create Catalog categories
crud.category_add(name="Soccer")
crud.category_add(name="Basketball")
crud.category_add(name="Baseball")
crud.category_add(name="Frisbee")
crud.category_add(name="Snowboarding")
crud.category_add(name="Rock Climbing")
crud.category_add(name="Football")
crud.category_add(name="Skating")
crud.category_add(name="Hockey")


# Create Category Items
crud.item_add(name="Stick", category_name="Hockey", user_id=1)
crud.item_add(name="Goggles", category_name="Snowboarding", user_id=1)
crud.item_add(name="Snowboard", category_name="Snowboarding", user_id=1)
crud.item_add(name="Two shinguards", category_name="Soccer", user_id=1)
crud.item_add(name="Shinguards", category_name="Soccer", user_id=1)
crud.item_add(name="Bat", category_name="Baseball", user_id=2)
crud.item_add(name="Jersey", category_name="Soccer", user_id=2)
crud.item_add(name="Soccer Cleats", category_name="Soccer", user_id=2)
crud.item_add(name="Frisbee", category_name="Frisbee", user_id=2)
print crud.items_count()
print "Successfully added Catalog categories, items and test users!"
