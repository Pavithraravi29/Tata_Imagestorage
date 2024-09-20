from app.database.models import db


def configure_database():
    db.bind(
        provider='postgres',
        user='postgres',
        password='password',
        host='localhost',
        database='ELimagestorage'
    )
    db.generate_mapping(create_tables=True)
    # db.execute("""
    #        SELECT create_hypertable('image_data', 'timestamp');
    #    """)