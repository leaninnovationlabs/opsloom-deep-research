"""
003_seed_guests_and_res

Revision ID: 0003_seed_guests_and_res
Revises: 0002_seed_data
Create Date: 2025-01-09
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003_seed_guests_and_res"
down_revision: Union[str, None] = "0002_seed_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()

    # -----------------------------
    # 1) SEED GUESTS, capturing each guest's UUID
    # -----------------------------
    guests = [
        ("Peter Griffin",        "peter.bigbelly@puffy.com",         "(715) 555-0101"),
        ("Lois Griffin",         "lois.lovehandles@chewmail.com",    "(715) 555-0102"),
        ("Chris Griffin",        "chris.cheeseburger@oddmail.net",   "(715) 555-0103"),
        ("Meg Griffin",          "meg.muffintop@puffy.com",          "(715) 555-0104"),
        ("Stewie Griffin",       "stewie.stuffed@breadmail.org",     "(715) 555-0105"),
        ("Brian Griffin",        "brian.bulge@plumpmail.com",        "(715) 555-0106"),
        ("Cleveland Brown",      "cleveland.cheese@puffy.com",       "(715) 555-0107"),
        ("Joe Swanson",          "joe.jellyroll@oddmail.net",        "(715) 555-0108"),
        ("Glenn Quagmire",       "glenn.glutton@chewmail.com",       "(715) 555-0109"),
        ("Bonnie Swanson",       "bonnie.butterball@plumpmail.com",  "(715) 555-0110"),
        ("Herbert",              "herbert.heavyhank@puffy.com",      "(715) 555-0111"),
        ("Carter Pewterschmidt", "carter.corpulent@oddmail.net",     "(715) 555-0112"),
        ("Barbara Pewterschmidt","barbara.breadstick@puffy.com",     "(715) 555-0113"),
        ("Mort Goldman",         "mort.megameal@chewmail.com",       "(715) 555-0114"),
        ("Neil Goldman",         "neil.double@plumpmail.com",        "(715) 555-0115"),
        ("Bruce",                "bruce.bratwurst@puffy.com",        "(715) 555-0116"),
        ("Tom Tucker",           "tom.tubby@breadmail.org",          "(715) 555-0117"),
        ("Diane Simmons",        "diane.doughy@oddmail.net",         "(715) 555-0118"),
        ("Seamus",               "seamus.seabiscuit@puffy.com",      "(715) 555-0119"),
        ("Angela",               "angela.ample@chewmail.com",        "(715) 555-0120"),
        ("Adam West",            "adam.appetite@plumpmail.com",      "(715) 555-0121"),
        ("Dr. Elmer Hartman",    "doc.extra@puffy.com",              "(715) 555-0122"),
        ("Evil Monkey",          "evil.expanded@oddmail.net",        "(715) 555-0123"),
        ("Connie D'Amico",       "connie.chocolate@breadmail.org",   "(715) 555-0124"),
        ("Jillian Russell",      "jillian.jello@chewmail.com",       "(715) 555-0125"),
        ("Horace",               "horace.hearty@puffy.com",          "(715) 555-0126"),
        ("GreasedUp Deaf Guy",   "greasedup.gigantic@oddmail.net",   "(715) 555-0127"),
        ("Bertram",              "bertram.bellybust@breadmail.org",  "(715) 555-0128"),
        ("Olivia Fuller",        "olivia.oversized@puffy.com",       "(715) 555-0129"),
        ("Mayor West",           "mayor.massive@plumpmail.com",      "(715) 555-0130"),
    ]

    # We'll store the generated guest_ids here in the same order.
    inserted_guest_ids = []

    insert_guest_stmt = sa.text(
        """
        INSERT INTO guests (full_name, email, phone)
        VALUES (:full_name, :email, :phone)
        RETURNING guest_id
        """
    )

    for (full_name, email, phone) in guests:
        result = conn.execute(
            insert_guest_stmt,
            dict(full_name=full_name, email=email, phone=phone),
        )
        # `RETURNING guest_id` yields a single row with the new UUID
        new_guest_id = result.scalar_one()
        inserted_guest_ids.append(new_guest_id)

    # -----------------------------
    # 2) SEED RESERVATIONS
    # -----------------------------
    #
    # We'll create 10 reservations for the first 10 guests and rooms 101..110.
    # (Ensure rooms 101..110 exist from your previous seeds.)
    reservations = [
        (0, 101, "2025-01-15", "2025-01-20", "confirmed"),
        (1, 102, "2025-01-16", "2025-01-21", "confirmed"),
        (2, 103, "2025-01-17", "2025-01-22", "confirmed"),
        (3, 104, "2025-01-18", "2025-01-23", "confirmed"),
        (4, 105, "2025-01-19", "2025-01-24", "confirmed"),
        (5, 106, "2025-01-20", "2025-01-25", "confirmed"),
        (6, 107, "2025-01-21", "2025-01-26", "confirmed"),
        (7, 108, "2025-01-22", "2025-01-27", "confirmed"),
        (8, 109, "2025-01-23", "2025-01-28", "confirmed"),
        (9, 110, "2025-01-24", "2025-01-29", "confirmed"),
    ]

    insert_res_stmt = sa.text(
        """
        INSERT INTO reservations (guest_id, room_id, check_in, check_out, status)
        VALUES (:guest_id, :room_id, :check_in, :check_out, :status)
        """
    )

    for (guest_idx, room_id, check_in, check_out, status) in reservations:
        # "guest_idx" is the index in inserted_guest_ids
        guest_uuid = inserted_guest_ids[guest_idx]
        conn.execute(
            insert_res_stmt,
            dict(
                guest_id=guest_uuid,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
                status=status,
            ),
        )


def downgrade():
    conn = op.get_bind()

    # 1) Remove the reservations referencing the 10 guest UUIDs we inserted 
    #    (the ones that actually got reservations).
    guest_ids_used_in_reservations = []

    # If you know the first 10 we inserted had reservations:
    # slice the first 10 guest UUIDs from 'inserted_guest_ids' in upgrade()
    # but we no longer have that list in downgrade. 
    # -> We either do the same queries or store them in a local variable 
    #    again if you want to keep it symmetrical.
    # This example just queries the DB. Alternatively, you can 
    # build a static list of those 10 emails or use a subselect, etc.

    # We'll do it by matching the known 10 emails from the top 10 guests:
    top_10_emails = [
        "peter.bigbelly@puffy.com",
        "lois.lovehandles@chewmail.com",
        "chris.cheeseburger@oddmail.net",
        "meg.muffintop@puffy.com",
        "stewie.stuffed@breadmail.org",
        "brian.bulge@plumpmail.com",
        "cleveland.cheese@puffy.com",
        "joe.jellyroll@oddmail.net",
        "glenn.glutton@chewmail.com",
        "bonnie.butterball@plumpmail.com",
    ]

    # Let's retrieve those actual guest_ids from the DB:
    rows = conn.execute(
        sa.text(
            """
            SELECT guest_id
            FROM guests
            WHERE email IN :emails
            """
        ),
        {"emails": tuple(top_10_emails)},
    )

    guest_ids_used_in_reservations = [r[0] for r in rows.fetchall()]

    if guest_ids_used_in_reservations:
        # We'll remove the reservations referencing those IDs
        in_clause = ", ".join(f"'{str(gid)}'" for gid in guest_ids_used_in_reservations)
        conn.execute(
            sa.text(f"DELETE FROM reservations WHERE guest_id IN ({in_clause})")
        )

    # 2) Finally, remove **all** guests we inserted (the entire 30). 
    #    We'll match by their emails since that's unique.
    all_emails = [
        "peter.bigbelly@puffy.com",
        "lois.lovehandles@chewmail.com",
        "chris.cheeseburger@oddmail.net",
        "meg.muffintop@puffy.com",
        "stewie.stuffed@breadmail.org",
        "brian.bulge@plumpmail.com",
        "cleveland.cheese@puffy.com",
        "joe.jellyroll@oddmail.net",
        "glenn.glutton@chewmail.com",
        "bonnie.butterball@plumpmail.com",
        "herbert.heavyhank@puffy.com",
        "carter.corpulent@oddmail.net",
        "barbara.breadstick@puffy.com",
        "mort.megameal@chewmail.com",
        "neil.double@plumpmail.com",
        "bruce.bratwurst@puffy.com",
        "tom.tubby@breadmail.org",
        "diane.doughy@oddmail.net",
        "seamus.seabiscuit@puffy.com",
        "angela.ample@chewmail.com",
        "adam.appetite@plumpmail.com",
        "doc.extra@puffy.com",
        "evil.expanded@oddmail.net",
        "connie.chocolate@breadmail.org",
        "jillian.jello@chewmail.com",
        "horace.hearty@puffy.com",
        "greasedup.gigantic@oddmail.net",
        "bertram.bellybust@breadmail.org",
        "olivia.oversized@puffy.com",
        "mayor.massive@plumpmail.com",
    ]

    conn.execute(
        sa.text(
            """
            DELETE FROM guests
            WHERE email IN :emails
            """
        ),
        {"emails": tuple(all_emails)},
    )
