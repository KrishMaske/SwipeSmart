def get_all_transactions():
    try:
        with get_connection() as c:
            c.execute('SELECT transaction_id, name, amount, date FROM transactions')
            rows = c.fetchall()
            transactions = []
            for row in rows:
                transactions.append({
                    "transaction_id": row[0],
                    "name": row[1],
                    "amount": row[2],
                    "date": row[3]
                })
        return transactions
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []

def get_transaction_by_month(year: int, month: int):
    try:
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        with get_connection() as c:
            c.execute('''
                SELECT transaction_id, name, amount, date 
                FROM transactions 
                WHERE date >= ? AND date < ?
            ''', (start_date, end_date))
            
            rows = c.fetchall()
            transactions = []
            for row in rows:
                transactions.append({
                    "transaction_id": row[0],
                    "name": row[1],
                    "amount": row[2],
                    "date": row[3]
                })
        return {"year": year, "month": month, "transactions": transactions}
    except Exception as e:
        print(f"Error fetching transactions for {year}-{month}: {e}")
        return {"year": year, "month": month, "transactions": []}

def get_monthly_summary(year: int, month: int):
    try:
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        with get_connection() as c:
            c.execute('''
                SELECT SUM(amount) 
                FROM transactions 
                WHERE date >= ? AND date < ?
            ''', (start_date, end_date))
            
            total = c.fetchone()[0]
        return {"year": year, "month": month, "total_amount": total if total else 0.0}
    except Exception as e:
        print(f"Error fetching monthly summary for {year}-{month}: {e}")
        return {"year": year, "month": month, "total_amount": 0.0}
    
def get_recent_transactions():
    try:
        with get_connection() as c:
            c.execute('''
                    SELECT transaction_id, name, amount, date
                    FROM transactions
                    ORDER BY date DESC
                    LIMIT 10
            ''')

            rows = c.fetchall()
        recent_transactions = []
        for row in rows:
            recent_transactions.append({
                "transaction_id": row[0],
                "name": row[1],
                "amount": row[2],
                "date": row[3]
            })
        
        return {"recent_transactions": recent_transactions}
    except Exception as e:
        print(f"Error fetching recent transactions")
        return {"recent_transactions": {}}