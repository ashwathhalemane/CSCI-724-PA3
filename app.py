import re
import json
import pymongo
from flask import Flask, request
from flask import render_template,redirect
from flask_pymongo import PyMongo
from flask import jsonify
from bson.json_util import dumps

app = Flask(__name__)

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
api_collection = db["APIs"]
mashup_collection = db["Mashups"]
members_collection = db["Members"]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api')
def api():
    read_api() 
    read_mashup()
    read_members()

    return "PARSING DONE..."

@app.route('/recipes', methods=['GET'])
def recipes():
    year = request.args.get('query')
    year = str(year)
    result = api_collection.find({'updated': {'$regex': year}}, {'title': 1, '_id': 0})
    print(result)
    result_list= []
    for res in result:
        result_list.append(res)
    response = json.dumps(result_list)
    return response

@app.route('/products', methods=['GET'])
def get_products():
    search_term = request.args.get('search')
    search_term = str(search_term)
    
    result_list = []
    
    result = api_collection.find({'protocols': {'$regex': search_term, '$options': 'i'}})
    
    for res in result:
        result_list.append(res)
    response = json.dumps(result_list)
    return response


# route for getting all APIs name using category
@app.route('/category', methods=['GET'])
def category():
    
    category = request.args.get('category')
    
    category = str(category)
    # print type of search_term to see if it is a string
    result_list = []
    
    result = api_collection.find({'category': {'$regex': category, '$options': 'i'}})
    
    for res in result:
        result_list.append(res)
    response = json.dumps(result_list)
    return response


@app.route('/rating_greater', methods=['GET'])
def get_api_by_rating_greater_than():
    rating = request.args.get('rating')
    rating = float(rating)
    rating_list = []

    result = api_collection.find({'rating': {'$gt': rating}})
    for res in result:
        rating_list.append(res)
    response = json.dumps(rating_list)
    return response


@app.route('/rating_less', methods=['GET'])
def get_api_by_rating_lower_than():
    rating = request.args.get('rating')
    rating = float(rating)
    rating_list = []

    result = api_collection.find({'rating': {'$lt': rating}})
    for res in result:
        rating_list.append(res)
    response = json.dumps(rating_list)
    return response

@app.route('/rating_equal', methods=['GET'])
def get_api_by_rating_equal_to():
    rating = request.args.get('rating')
    rating = float(rating)
    rating_list = []

    result = api_collection.find({'rating': {'$eq': rating}})
    for res in result:
        rating_list.append(res)
    response = json.dumps(rating_list)
    return response


@app.route('/tags'  , methods=['GET'])
def get_api_by_tags():
    # since tags is an array in the database, we need to use $in to search
    tag = request.args.get('tags')
    tag = str(tag)
    tag_list = []

    result = api_collection.find({'tags': {'$in': [tag]}})
    for res in result:
        # print(res)
        tag_list.append(res)
    response = json.dumps(tag_list)
    return response

@app.route('/mashups_by_year' , methods=['GET'])
def get_mashup_by_year():
    year = request.args.get('year')
    year = str(year)

    mashup_list = []
    result = mashup_collection.find({'updated': {'$regex': year}})
    for res in result:
        # print(res)
        mashup_list.append(res)
    response = json.dumps(mashup_list)
    return response

@app.route('/mashups_by_usedAPIs', methods=['GET'])
def get_mashup_by_api():
    api = request.args.get('usedAPIs')
    api = str(api)
    api_list = []
    escaped_api = re.escape(api)
    regex_string = escaped_api.replace("\\(", "\\\\(").replace("\\)", "\\\\)")
    result = mashup_collection.find({'apis': {'$regex': regex_string}})
    for res in result:
        # print(res)
        api_list.append(res)
    response = json.dumps(api_list)
    return response

@app.route('/mashup_usedTags')
def get_mashup_by_tags():
    tag = request.args.get('usedTags')
    tag = str(tag)
    tag_list = []

    result = mashup_collection.find({'tags': {'$in': [tag]}})
    for res in result:
        # print(res)
        tag_list.append(res)
    response = json.dumps(tag_list)
    return response

@app.route('/api_keywords' , methods=['GET'])
def get_api_by_keywords():
    keywords = request.args.get('keywords')
    keywords = keywords.split(',')
    

    for keyword in keywords:
        result = api_collection.find({'$and': [{'$or': [{'title': {'$regex': keyword, '$options': 'i'}},
                                                       {'summary': {'$regex': keyword, '$options': 'i'}},
                                                       {'description': {'$regex': keyword, '$options': 'i'}}]}]})
        
        # print("results are: " + str(result))

    result_list = []
    for res in result:
        # print(res)
        result_list.append(res)
    response = json.dumps(result_list)
    return response

@app.route('/mashup_keywords', methods=['GET'])    
def get_mash_by_keywords():
    keywords = request.args.get('keywordsMashups')

    keywords = keywords.split(',')
    
    for keyword in keywords:
        result = mashup_collection.find({'$and': [{'$or': [{'title': {'$regex': keyword, '$options': 'i'}},
                                                       {'summary': {'$regex': keyword, '$options': 'i'}},
                                                       {'description': {'$regex': keyword, '$options': 'i'}}]}]})
        # print("results are: " + str(result))
    
    result_list = []
    for res in result:
        # print(res)
        result_list.append(res)
    response = json.dumps(result_list)
    return response

def read_api():    
    api_data = []
    with open('api.txt', 'r') as f:
            
        for line in f:
            fields = line.strip().split('$#$')
            api = {
                '_id': fields[0],
                'title': fields[1],
                'summary': fields[2],
                'rating' : float(fields[3]) if fields[3] else None,
                'name': fields[4],
                'label': fields[5],
                'author': fields[6],
                'description': fields[7],
                'type': fields[8],
                'downloads': fields[9],
                'useCount': fields[10],
                'sampleUrl': fields[11],
                'downloadUrl': fields[12],
                'dateModified': fields[13],
                'remoteFeed': fields[14],
                'numComments': fields[15],
                'commentsUrl': fields[16],
                'tags': fields[17].split('###'),
                'category': fields[18],
                'protocols': fields[19],
                'serviceEndpoint': fields[20],
                'version': fields[21],
                'wsdl': fields[22],
                'dataFormats': fields[23],
                'apiGroups': fields[24],
                'example': fields[25],
                'clientInstall': fields[26],
                'authentication': fields[27],
                'ssl': fields[28],
                'readonly': fields[29],
                'VendorApiKits': fields[30],
                'CommunityApiKits': fields[31],
                'blog': fields[32],
                'forum': fields[33],
                'support': fields[34],
                'accountReq': fields[35],
                'commercial': fields[36],
                'provider': fields[37],
                'managedBy': fields[38],
                'nonCommercial': fields[39],
                'dataLicensing': fields[40],
                'fees': fields[41],
                'limits': fields[42],
                'terms': fields[43],
                'company': fields[44],
                # get first 4 characters of the updated field
                'updated': fields[45][:4]
                }
            api_data.append(api)

        
    
    result = api_collection.insert_many(api_data)
    print(result.inserted_ids)


def read_mashup():
    mashup_data = []
    with open('mashup.txt', 'r') as f:
            
        for line in f:
            fields = line.strip().split('$#$')
            mashup = {
                'id': fields[0],
                'title': fields[1],
                'summary': fields[2],
                # 'rating': float(fields[3]),
                'rating' : float(fields[3]) if fields[3] else None,
                'name': fields[4],
                'label': fields[5],
                'author': fields[6],
                'description': fields[7],
                'type': fields[8],
                'downloads': fields[9],
                'useCount': fields[10],
                'sampleUrl': fields[11],
                'dateModified': fields[12],
                'numComments': fields[13],
                'commentsUrl': fields[14],
                'tags': fields[15].split('###'),
                # store apis like Shopzilla(http://www.programmableweb.com/api/shopzilla) instead of Shopzilla in the database
                # 'apis': fields[16].split('$$$')[0] + '(' + fields[16].split('$$$')[1] + ')',
                'updated': fields[17][:4]
                }
            mashup_data.append(mashup)


    result = mashup_collection.insert_many(mashup_data)
    print(result.inserted_ids)
    # except pymongo.errors.BulkWriteError as e:
    #     print(e.details)
    #     for operation in e.details['writeErrors']:
    #         failed_operations.append(operation)
    #     print(failed_operations)
    
    # if failed_operations:
    #     print("failed operations: " + str(failed_operations))
    #     print("retrying failed operations")
    #     result = mashup_collection.bulk_write(failed_operations, ordered=False)
    #     print(result.inserted_ids)

def read_members():
    members_data = []
    with open('members.txt', 'r') as f:
            
        for line in f:
            fields = line.strip().split('$#$')
            members = {
                '_id': fields[0],
                'name': fields[1],
                'profile_url': fields[2],
                'Latitude': fields[5],
                'Longitude': fields[6],
                'updated': fields[9][:4]
                }
            members_data.append(members)

    result = members_collection.insert_many(members_data, ordered=False)
    print(result.inserted_ids)


if __name__ == '__main__':
    # read_api()
    # read_mashup()
    # read_members()

    app.run(debug=True)