from app.models import BloodGroup


def populate_blood_group_table(db):
    """
    Function to populate the blood group table
    :param db: db context
    :return: None
    """
    names = ['0', 'A1', 'B2', 'AB']
    bl_group = [BloodGroup(name=names[i], rh=0) for i in range(4)]
    bl_group = bl_group + [BloodGroup(name=names[i], rh=1) for i in range(4)]
    for group in bl_group:
        db.session.add(group)
    db.session.commit()