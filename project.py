from flask import Flask, render_template, url_for, request, jsonify
import crud

app = Flask(__name__)

@app.route('/')
@app.route('/catalog')
def catalog():
    categories = crud.category_all()
    items = crud.items_latest()[:9]
    return render_template('catalog.html',
                           categories=categories, items=items)

@app.route('/catalog/<category_name>/<item_name>')
def categoryItem(category_name, item_name):
    item = crud.item_byname(category_name, item_name)
    return render_template('category_item.html',
                           category_name=category_name,
                           item=item)

@app.route('/catalog/<category_name>/items')
def categoryItems(category_name):
    categories = crud.category_all()
    cat_items = crud.items_bycat(category_name)
    return render_template('category_items.html',
                           categories=categories,
                           category_name=category_name,
                           items=cat_items)

@app.route('/catalog.json')
def catalogJSON():
    pass
    categories = crud.category_all()
    return jsonify(Category=[c.serialize for c in categories])

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
    back_url = '/'
    categories = ("First", "Second", "Third")
    return render_template('edititem.html',
                           item_name=item_name,
                           item_description='some text',
                           categories=categories,
                           back_url=back_url)

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
    back_url = '/'
    return render_template('deleteitem.html',
                           item_name=item_name,
                           back_url=back_url)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
