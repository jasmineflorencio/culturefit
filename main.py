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

def generate_random_user_name():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(8))

def create_user(company_id, position, identity_ids):
    # create random user name to identify user
    user_name = generate_random_user_name()

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

@app.route('/users')
def get_users():
    with db.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users")
            user_records = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            users = []

            for user_record in user_records:
                user = dict(zip(column_names, user_record))
                users.append(user)

            return jsonify(users)

# TODO: check url query params to narrow results
@app.route('/reviews')
def get_reviews():
    with db.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM reviews")
            review_records = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            reviews = []

            # turn db result into key, value pair
            for review_record in review_records:
                review = dict(zip(column_names, review_record))
                reviews.append(review)

            return jsonify(reviews)

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
    # get or create company
    company_name = request.get_json().get("company_name")
    company_id = get_or_create_company(company_name)

    # create a user
    position = request.get_json().get("position")
    identity_ids = request.get_json().get("identities")
    user_id = create_user(company_id, position, identity_ids)

    # create a review
    sentiment = request.get_json().get("sentiment")
    title = request.get_json().get("title")
    body = request.get_json().get("body")

    with db.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO reviews (user_id, sentiment, title, body) VALUES ('{user_id}', '{sentiment}', '{title}', '{body}')")
            connection.commit()

            return jsonify({"message": 'Experience submitted'})




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
