from flask import Flask, request, jsonify
import db
import random
import string

app = Flask(__name__)

@app.route('/')
def hello():
    return "What's your culture fit?"

def get_or_create_company(company_name):
    with db.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM companies WHERE name = '{company_name}'")
            company_record = cursor.fetchone()
            if company_record:
                #return the company id
                return company_record[0]
            else:
                cursor.execute(f"INSERT INTO companies (name) VALUES ('{company_name}')")
                connection.commit()
                cursor.execute(f"SELECT * FROM companies WHERE name = '{company_name}'")
                company_record = cursor.fetchone()
                return company_record[0]

def create_user(company_id, position, identity_ids):
    #create random user name to identify user
    letters = string.ascii_lowercase
    user_name = ''.join(random.choice(letters) for i in range(8))

    with db.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO users (company_id, name, position) VALUES ({company_id}, '{user_name}', '{position}')")
            connection.commit()
            cursor.execute(f"SELECT id FROM users WHERE name = '{user_name}'")
            user_record = cursor.fetchone()
            user_id = user_record[0]

            for identity_id in identity_ids:
                cursor.execute(f"INSERT INTO user_identities (user_id, identity_id) VALUES ('{user_id}', '{identity_id}')")
                connection.commit()

            return user_id

'''
expected json format
{
    company_name: str
    sentiment: str
    title: str
    body: str
    identities: array of int
    position: str
}
'''
@app.route('/reviews', methods=["POST"])
def create_review():
    company_name = request.get_json().get("company_name")
    company_id = get_or_create_company(company_name)
    position = request.get_json().get("position")
    identity_ids = request.get_json().get("identities")
    user_id = create_user(company_id, position, identity_ids)
    sentiment = request.get_json().get("sentiment")
    title = request.get_json().get("title")
    body = request.get_json().get("body")

    with db.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO reviews (user_id, sentiment, title, body) VALUES ('{user_id}', '{sentiment}', '{title}', '{body}')")
            connection.commit()

            return jsonify({message: 'Experience submitted'})




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

'''
company name
company experience (neg, neut, pos)
exp title
exp body
identities
'''
