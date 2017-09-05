import json
import decimal
from .models import Product

# Takes the standard JSON representation of these arrays and returns them as an actual array of Product
def parseJsonProductList(jsonstring):
    jsonDict = json.loads(jsonstring)
    resultList = []

    for productDict in jsonDict:
        product = Product()
        product.product_id = productDict['product_id']
        product.product_name = productDict['product_name']
        product.product_price = decimal.Decimal(productDict['product_price'])
        product.product_stock = productDict['product_stock']
        product.product_stockApplies = productDict['product_stockApplies']
        resultList.append(product)

    return resultList

# This is bodgy...
# I have to do the array constructs manually because otherwise it would turn into an array of strings...
def productListToJson(productList):
    jsonString = "["

    for product in productList:
        if jsonString is not "[":
            jsonString += ","

        cleanDict = product.__dict__
        # This state thing is a hidden Django object that can't be serialized and doesn't need to be either
        del cleanDict['_state']
        cleanDict['product_price'] = str(cleanDict['product_price'])
        jsonString += json.dumps(cleanDict)

    jsonString += "]"

    return jsonString
