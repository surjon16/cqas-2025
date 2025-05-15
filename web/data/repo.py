# from data.repositories.common   import CommonRepo as common
from data.repositories  import common
from data               import db
from random             import randint, choice
from faker              import Faker

class Repository:

    def __init__(self):
        self.fake = Faker()
        self.cm_util = common

    def get_common_util(self):
        return self.cm_util

    # FACTORY / DUMMY
    def create_dummy_users(self):
        users = []
        for _ in range(10):
            user = self.cm_util.User(
                name=self.fake.name(),
                email=self.fake.email(),
                phone=self.fake.phone_number(),
                password=self.fake.password(),
                role=choice(['customer', 'guest']),
            )
            users.append(user) 
        db.session.bulk_save_objects(users)
        db.session.commit()

    def create_dummy_vehicles(self):
        vehicles = []
        users = self.cm_util.User.query.all()  # Get all users from the database
        for _ in range(10):
            vehicle = self.cm_util.Vehicle(
                user_id=choice(users).id,
                plate_number=self.fake.license_plate(),
                model=self.fake.word(),
                type=choice(['Sedan', 'SUV', 'Truck', 'Van'])
            )
            vehicles.append(vehicle)
        db.session.bulk_save_objects(vehicles)
        db.session.commit()

    def create_dummy_appointments(self):
        appointments = []
        vehicles = self.cm_util.Vehicle.query.all()
        users = self.cm_util.User.query.all()
        staff = self.cm_util.Staff.query.all()
        for _ in range(10):
            appointment = self.cm_util.Appointment(
                user_id=choice(users).id,
                staff_id=choice(staff).id,
                vehicle_id=choice(vehicles).id,
                service_type=choice(['Full Wash', 'Exterior Wash', 'Interior Clean', 'Detailing']),
                appointment_date=self.fake.date_time_this_year(),
                status=choice(['Pending', 'Completed', 'Cancelled']),
                payment_status=choice(['Paid', 'Unpaid'])
            )
            appointments.append(appointment)
        db.session.bulk_save_objects(appointments)
        db.session.commit()

    def create_dummy_payments(self):
        payments = []
        appointments = self.cm_util.Appointment.query.all()
        for _ in range(10):
            payment = self.cm_util.Payment(
                appointment_id=choice(appointments).id,
                amount=randint(50, 150),
                payment_method=choice(['Cash', 'Card', 'Online']),
                payment_status=choice(['Pending', 'Paid']),
                transaction_date=self.fake.date_time_this_year()
            )
            payments.append(payment)
        db.session.bulk_save_objects(payments)
        db.session.commit()

    def create_dummy_notifications(self):
        notifications = []
        users = self.cm_util.User.query.all()
        for _ in range(10):
            notification = self.cm_util.Notification(
                user_id=choice(users).id,
                message=self.fake.sentence(),
                status=choice(["Unread", "Read"]),
                created_at=self.fake.date_time_this_year()
            )
            notifications.append(notification)
        db.session.bulk_save_objects(notifications)
        db.session.commit()

    def create_dummy_loyalties(self):
        loyalties = []
        users = self.cm_util.User.query.all()
        for _ in range(10):
            loyalty = self.cm_util.Loyalty(
                user_id=choice(users).id,
                points_earned=randint(10, 50),
                points_spent=randint(0, 20),
                updated_at=self.fake.date_time_this_year() 
            )
            loyalties.append(loyalty) 
        db.session.bulk_save_objects(loyalties)
        db.session.commit()

    def create_dummy_services(self):
        services = []
        for _ in range(10):
            service = self.cm_util.Service(
                name=choice(['Full Wash', 'Exterior Wash', 'Interior Clean', 'Detailing']),
                description=self.fake.sentence(),
                price=randint(20, 100)
            )
            services.append(service)
        db.session.bulk_save_objects(services)
        db.session.commit()

    def create_dummy_queues(self):
        queues = []
        appointments = self.cm_util.Appointment.query.all()
        for _ in range(10):
            queue = self.cm_util.Queue(
                appointment_id=choice(appointments).id,
                position=randint(1, 20),
            )
            queues.append(queue)
        db.session.bulk_save_objects(queues)
        db.session.commit()

    def create_dummy_staff(self):
        staff = []
        staff_member = self.cm_util.Staff(
            name=self.fake.name(),
            email=self.fake.email(),
            role='Admin',
        ) 
        staff.append(staff_member)
        staff_member = self.cm_util.Staff(
            name=self.fake.name(),
            email=self.fake.email(),
            role='Manager',
        ) 
        staff.append(staff_member)
        for _ in range(10):
            staff_member = self.cm_util.Staff(
                name=self.fake.name(),
                email=self.fake.email(),
                role=choice(['Cashier', 'Washer', 'Cleaner']),
            ) 
            staff.append(staff_member)
        db.session.bulk_save_objects(staff)
        db.session.commit()

    def create_dummy_feedbacks(self):
        feedbacks = []
        users = self.cm_util.User.query.all()
        appointments = self.cm_util.Appointment.query.all()
        for _ in range(10):
            feedback = self.cm_util.Feedback(
                user_id=choice(users).id,
                appointment_id=choice(appointments).id,
                rating=randint(1, 5),
                comment=self.fake.sentence(),
                created_at=self.fake.date_time_this_year()
            )
            feedbacks.append(feedback)
        db.session.bulk_save_objects(feedbacks)
        db.session.commit()

    def start_factory(self):
        self.create_dummy_users()
        self.create_dummy_vehicles()
        self.create_dummy_staff()
        self.create_dummy_appointments()
        self.create_dummy_payments()
        self.create_dummy_notifications()
        self.create_dummy_loyalties()
        self.create_dummy_services()
        self.create_dummy_queues()
        self.create_dummy_feedbacks()