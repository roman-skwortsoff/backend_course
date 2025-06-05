from datetime import date
from sqlalchemy import select, literal, label, union_all, func

from app.models.bookings import BookingsOrm
from app.models.rooms import RoomsOrm


def rooms_ids_for_booking(
    date_from: date,
    date_to: date,
    hotel_id: int | None = None,
):
    """
    with events AS (
        SELECT
            room_id,
            date_from AS event_date,
            +1 AS delta
        FROM bookings
        WHERE date_from < '2025-05-21' AND date_to > '2025-05-07'
        UNION ALL
        SELECT
            room_id,
            date_to AS event_date,
            -1 AS delta
        FROM bookings
        WHERE date_from < '2025-05-21' AND date_to > '2025-05-07'
    ),
    running_totals AS (
        SELECT
            room_id,
            event_date,
            SUM(delta) OVER (PARTITION BY room_id ORDER BY event_date) AS active_bookings
        FROM events
    ),
    max_rooms_used AS (
        SELECT
            room_id,
            MAX(active_bookings) AS rooms_booked
        FROM running_totals
        GROUP BY room_id
    ),
    rooms_table AS (
        SELECT
            rooms.id AS room_id,
            rooms.quantity - COALESCE(max_rooms_used.rooms_booked, 0) AS rooms_left
        FROM rooms
        LEFT JOIN max_rooms_used ON rooms.id = max_rooms_used.room_id
        WHERE rooms.id IN (
            SELECT id
            FROM rooms
            WHERE hotel_id = 5
        )
    )
    SELECT *
    FROM rooms_table
    WHERE rooms_left > 0;
    """

    events_from = (
        select(
            BookingsOrm.room_id,
            label("event_date", BookingsOrm.date_from),
            label("delta", literal(1)),
        )
        .select_from(BookingsOrm)
        .filter(
            BookingsOrm.date_from < date_to,
            BookingsOrm.date_to > date_from,
        )
    )

    events_to = (
        select(
            BookingsOrm.room_id,
            label("event_date", BookingsOrm.date_to),
            label("delta", literal(-1)),
        )
        .select_from(BookingsOrm)
        .filter(
            BookingsOrm.date_from < date_to,
            BookingsOrm.date_to > date_from,
        )
    )

    events = union_all(events_from, events_to).subquery("events")

    running_totals = select(
        events.c.room_id,
        events.c.event_date,
        func.sum(events.c.delta)
        .over(partition_by=events.c.room_id, order_by=events.c.event_date)
        .label("active_bookings"),
    ).cte(name="r_totals")

    max_rooms_used = (
        select(
            running_totals.c.room_id,
            func.max(running_totals.c.active_bookings).label("rooms_booked"),
        )
        .select_from(running_totals)
        .group_by(running_totals.c.room_id)
        .cte(name="rooms_used")
    )

    if hotel_id is not None:
        hotel_filter = RoomsOrm.hotel_id == hotel_id
    else:
        hotel_filter = True

    rooms_table = (
        select(
            RoomsOrm.id.label("room_id"),
            (RoomsOrm.quantity - func.coalesce(max_rooms_used.c.rooms_booked, 0)).label(
                "rooms_left"
            ),
        )
        .select_from(RoomsOrm)
        .filter(hotel_filter)
        .outerjoin(max_rooms_used, RoomsOrm.id == max_rooms_used.c.room_id)
        .cte(name="rooms_table")
    )

    rooms_ids_to_get = select(rooms_table.c.room_id).filter(
        rooms_table.c.rooms_left > 0
    )

    return rooms_ids_to_get
