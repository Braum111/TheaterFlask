def get_average_ticket_price(play_id, cursor):
    cursor.execute("SELECT AverageTicketPrice(%s)", (play_id,))
    result = cursor.fetchone()
    return result  # возвращаем результат как есть

def get_occupancy_rate(performance_id, cursor):
    cursor.execute("SELECT OccupancyRate(%s)", (performance_id,))
    result = cursor.fetchone()
    return result  # возвращаем результат как есть

def get_total_tickets_sold(play_id, cursor):
    cursor.execute("SELECT TotalTicketsSold(%s)", (play_id,))
    result = cursor.fetchone()
    return result  # возвращаем результат как есть
