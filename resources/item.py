from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    get_jwt_identity,
    fresh_jwt_required,
)
from models.item import ItemModel


class Item(Resource):

    parser = reqparse.RequestParser()
    # make sure only argument "price" is seen, all others will be ignored
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help="This field can not be left blank!",
    )
    parser.add_argument(
        "store_id",
        type=int,
        required=True,
        help="Every item needs a store id",
    )

    @jwt_required
    def get(self, name):

        item = ItemModel.find_by_name(name)
        if item:
            return item.json()

        return {"message": "Item not found"}, 404

    @fresh_jwt_required
    def post(self, name):

        if ItemModel.find_by_name(name):
            return {
                "message": f"An item with name '{name}' already exists."
            }, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {
                "message": "An error occured inserting the item."
            }, 500  # Internal Server Error

        return item.json(), 201  # Created

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": "Admin privilege is required"}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {"message": "Item deleted"}

    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
            item.store_id = data["store_id"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()
        return item.json()


class Itemlist(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()  # check if the user is login
        items = [x.json() for x in ItemModel.find_all()]
        if user_id:
            return {"items": items}, 200
        return {
            "items": [item["name"] for item in items],
            "message": "For more data, please login.",
        }, 200
