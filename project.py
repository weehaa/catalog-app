from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/catalog')
def catalog():
    # restaurants = db.restaurants()
    # return render_template('restaurants.html', restaurants=restaurants)
    # return "Main page"
    categories = ("first", "second", "third")
    items = ("1st", "2nd", "3rd")
    return render_template('catalog.html', categories=categories, items=items)

@app.route('/catalog/<category_name>/items')
def categoryItems(category_name):
    # restaurant = db.restaurant_byid(restaurant_id)
    # items = db.menuitems(restaurant.id)
    return "Page for {category_name} items".format(category_name=category_name)

@app.route('/catalog/<category_name>/<item_name>/JSON')
def categoryItemJSON(category_name, item_name):
    pass
    # item = db.menuitem_byid(menu_id)
    # return jsonify(MenuItem=item.serialize)

@app.route('/catalog/<category_name>/new/', methods=['GET','POST'])
def addItem(category_name):
    # if request.method == 'POST':
    #     db.add_menuitem(request.form['name'], restaurant_id)
    #     flash("new item created!")
    #     return redirect(url_for('restaurantMenu',
    #                             restaurant_id=restaurant_id))
    # else:
    #     return render_template('newmenuitem.html',
    #                            restaurant_id=restaurant_id)
    return "Page for a new item in a {category_name} category". \
           format(category_name=category_name)


@app.route('/catalog/<item_name>/edit/',
           methods=['GET','POST'])
def editItem(item_name):
    # menuitem = db.menuitem_byid(menu_id)
    # if request.method == 'POST':
    #     db.update_menuitem(request.form['name'], restaurant_id)
    #     return redirect(url_for('restaurantMenu',
    #                             restaurant_id=restaurant_id))
    # else:
    #     return render_template('editmenuitem.html',
    #                            restaurant_id=restaurant_id,
    #                            menu=menuitem)
    return "Page for a editting an item {item_name}". \
           format(item_name=item_name)

@app.route('/catalog/<item_name>/delete/',
           methods=['GET','POST'])
def deleteItem(item_name):
    # menuitem = db.menuitem_byid(menu_id)
    # if request.method == 'POST':
    #     db.delete_menuitem(menuitem)
    #     flash("item deleted!")
    #     return redirect(url_for('restaurantMenu',
    #                             restaurant_id=restaurant_id))
    # else:
    #     return render_template('deletemenuitem.html',
    #                            restaurant_id=restaurant_id,
    #                            item=menuitem)
    return "Page for  deleting an item {item_name}". \
           format(item_name=item_name)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
