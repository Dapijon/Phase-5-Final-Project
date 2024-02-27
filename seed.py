from decimal import Decimal
from faker import Faker
from app import create_app, db
from app.models import User, Transaction


fake = Faker()


def generate_fake_user():
    return User(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        dob=fake.date_of_birth(),
        email=fake.email(),
        national_ID=fake.uuid4(),
        phoneNumber=fake.phone_number(),
        password=fake.password(),
        balance=Decimal(fake.random_number(3)),
        transaction_password=fake.random_number(4),
    )


def seed_fake_users(num_users):
    fake_users = [generate_fake_user() for _ in range(num_users)]
    db.session.add_all(fake_users)
    db.session.commit()


def seed_fake_transactions(num_transactions):
    users = User.query.all()

    for _ in range(num_transactions):
        sender = fake.random_element(users)
        receiver = fake.random_element(users)

        while receiver == sender:
            receiver = fake.random_element(users)

        amount = Decimal(fake.random_number(2))

        try:
            new_transaction = Transaction(
                sender=sender,
                receiver=receiver,
                amount=amount
            )
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as e:
            print(f"Error adding fake transaction: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()

        seed_fake_users(10)
        seed_fake_transactions(20)
