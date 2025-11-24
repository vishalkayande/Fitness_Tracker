from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from config import db_config
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import math

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key_here'  # Change this to any random strong string


# ------------------ DATABASE CONNECTION ------------------
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn


# ------------------ CALORIE CALCULATION FUNCTIONS ------------------

# Fruit calories per 100g (scientific values from USDA)
FRUIT_CALORIES = {
    'apple': 52, 'apples': 52,
    'banana': 89, 'bananas': 89,
    'orange': 47, 'oranges': 47,
    'mango': 60, 'mangos': 60, 'mangoes': 60,
    'grapes': 69, 'grape': 69,
    'watermelon': 30, 'watermelons': 30,
    'strawberry': 32, 'strawberries': 32,
    'blueberry': 57, 'blueberries': 57,
    'pineapple': 50, 'pineapples': 50,
    'papaya': 43, 'papayas': 43,
    'kiwi': 61, 'kiwis': 61, 'kiwi fruit': 61,
    'pear': 57, 'pears': 57,
    'peach': 39, 'peaches': 39,
    'plum': 46, 'plums': 46,
    'cherry': 50, 'cherries': 50,
    'avocado': 160, 'avocados': 160,
    'guava': 68, 'guavas': 68,
    'pomegranate': 83, 'pomegranates': 83,
    'dragon fruit': 60, 'dragonfruit': 60,
    'lychee': 66, 'lychees': 66,
    'coconut': 354, 'coconuts': 354,
    'cranberry': 46, 'cranberries': 46,
    'raspberry': 52, 'raspberries': 52,
    'blackberry': 43, 'blackberries': 43,
    'lemon': 29, 'lemons': 29,
    'lime': 30, 'limes': 30,
    'grapefruit': 42, 'grapefruits': 42,
    'apricot': 48, 'apricots': 48,
    'fig': 74, 'figs': 74,
    'date': 282, 'dates': 282,
}

def get_fruit_calories(food_name, portion_weight_g=100):
    """
    Get calories for fruit based on name.
    Returns calories per portion_weight_g (default 100g).
    For average serving sizes, we'll use standard portions:
    - Apple/Orange: ~150g
    - Banana: ~120g
    - Small fruits (berries): ~100g
    """
    food_lower = food_name.lower().strip()
    
    # Check exact match first
    if food_lower in FRUIT_CALORIES:
        calories_per_100g = FRUIT_CALORIES[food_lower]
        return round(calories_per_100g * (portion_weight_g / 100), 1)
    
    # Check if fruit name is contained in the string
    for fruit, calories_per_100g in FRUIT_CALORIES.items():
        if fruit in food_lower:
            # Adjust portion based on fruit type
            if fruit in ['apple', 'apples', 'orange', 'oranges', 'pear', 'pears']:
                portion = 150  # Medium fruit ~150g
            elif fruit in ['banana', 'bananas']:
                portion = 120  # Medium banana ~120g
            elif fruit in ['avocado', 'avocados']:
                portion = 150  # Medium avocado ~150g
            elif fruit in ['strawberry', 'strawberries', 'blueberry', 'blueberries', 
                          'raspberry', 'raspberries', 'blackberry', 'blackberries']:
                portion = 100  # Cup of berries ~100g
            else:
                portion = portion_weight_g  # Use default or provided portion
            
            return round(calories_per_100g * (portion / 100), 1)
    
    return None  # Not a known fruit


# MET (Metabolic Equivalent of Task) values for exercises
# MET value * weight(kg) * duration(hours) = calories burned
EXERCISE_MET_VALUES = {
    'walking': 3.5,  # Walking at moderate pace
    'walking slow': 2.0,
    'walking fast': 5.0,
    'running': 11.0,  # Running at 8 km/h
    'running slow': 8.0,  # Jogging
    'running fast': 13.0,  # Running at 10+ km/h
    'swimming': 8.0,  # Swimming general
    'swimming slow': 6.0,
    'swimming fast': 10.0,
    'cycling': 8.0,  # Cycling moderate effort
    'cycling slow': 4.0,
    'cycling fast': 10.0,
    'jogging': 7.0,
    'jumping rope': 12.0,
    'dancing': 6.0,
    'yoga': 3.0,
    'weight lifting': 6.0,
    'aerobics': 7.0,
    'tennis': 7.0,
    'basketball': 8.0,
    'soccer': 7.0,
    'hiking': 6.0,
    'climbing': 8.0,
}

def calculate_calories_burned(activity, duration_minutes, weight_kg, height_cm=None, age=None, gender=None):
    """
    Calculate calories burned during exercise using MET values.
    Formula: MET * weight(kg) * time(hours) = calories burned
    
    For more accuracy with BMR adjustment (optional):
    - Uses Harris-Benedict or Mifflin-St Jeor equation
    - But MET values are simpler and widely used
    
    Args:
        activity: Exercise type (e.g., 'walking', 'running')
        duration_minutes: Exercise duration in minutes
        weight_kg: User's weight in kg
        height_cm: User's height in cm (optional, for BMR adjustment)
        age: User's age (optional, for BMR adjustment)
        gender: 'male' or 'female' (optional, for BMR adjustment)
    
    Returns:
        Calories burned (float)
    """
    activity_lower = activity.lower().strip()
    
    # Get MET value
    met_value = None
    for key, value in EXERCISE_MET_VALUES.items():
        if key in activity_lower:
            met_value = value
            break
    
    # Default MET if not found
    if met_value is None:
        met_value = 5.0  # Moderate activity default
    
    # Convert duration to hours
    duration_hours = duration_minutes / 60.0
    
    # Basic calculation: MET * weight * time
    calories = met_value * weight_kg * duration_hours
    
    # Optional: Adjust based on height and age for more accuracy
    # This is a simplified adjustment factor
    if height_cm and age:
        # BMI factor adjustment (optional refinement)
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2)
        
        # Slight adjustment: heavier people burn slightly more per MET unit
        # This is a simplified approximation
        if bmi > 25:
            calories *= 1.05  # Slight increase for higher BMI
        elif bmi < 18.5:
            calories *= 0.95  # Slight decrease for lower BMI
    
    return round(calories, 1)


def calculate_tracking_streak(report_entries):
    """
    Calculate consecutive days (from most recent) with any logged activity.
    """
    streak = 0
    for entry in reversed(report_entries):
        if entry['calories_in'] or entry['calories_out'] or entry['exercise_minutes']:
            streak += 1
        else:
            break
    return streak


# ------------------ HOME PAGE ------------------
@app.route('/')
def index():
    return render_template('index.html')


# ------------------ REGISTER USER ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        age = request.form.get('age', '0').strip()
        height = request.form.get('height', '0').strip()
        weight = request.form.get('weight', '0').strip()

        # Validate and convert numeric fields
        try:
            age = int(age) if age else None
            height = float(height) if height else None
            weight = float(weight) if weight else None
        except ValueError:
            age = None
            height = None
            weight = None

        # Hash password before storing
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return "Email already registered. Please login instead."

        # Insert new user with profile data
        cursor.execute(
            "INSERT INTO users (name, email, password, age, height, weight) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, hashed_password, age, height, weight)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to login page after successful registration
        return redirect(url_for('login'))

    return render_template('register.html')


# ------------------ LOGIN USER ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        is_valid = False
        if user:
            # Preferred: hashed check
            try:
                if check_password_hash(user['password'], password):
                    is_valid = True
            except Exception:
                is_valid = False
            # Legacy/plain-text support (no DB change)
            if not is_valid and user.get('password') == password:
                is_valid = True

        if is_valid:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials. Try again.")

    return render_template('login.html')


# ------------------ DASHBOARD ------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_name = session['user_name']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Today's totals
        try:
            cursor.execute("""
                SELECT IFNULL(SUM(calories), 0) AS total_calories, COUNT(*) AS items
                FROM food_log
                WHERE user_id = %s AND DATE(log_date) = CURDATE()
            """, (session['user_id'],))
            today = cursor.fetchone() or {"total_calories": 0, "items": 0}
        except mysql.connector.Error:
            cursor.execute("""
                SELECT IFNULL(SUM(calories), 0) AS total_calories, COUNT(*) AS items
                FROM food_log
                WHERE user_id = %s
            """, (session['user_id'],))
            today = cursor.fetchone() or {"total_calories": 0, "items": 0}

        # Today's burned calories
        try:
            cursor.execute("""
                SELECT IFNULL(SUM(calories_burned), 0) AS total_burned
                FROM exercise_log
                WHERE user_id = %s AND DATE(log_date) = CURDATE()
            """, (session['user_id'],))
            today_burned_row = cursor.fetchone() or {"total_burned": 0}
        except mysql.connector.Error:
            cursor.execute("""
                SELECT IFNULL(SUM(calories_burned), 0) AS total_burned
                FROM exercise_log
                WHERE user_id = %s
            """, (session['user_id'],))
            today_burned_row = cursor.fetchone() or {"total_burned": 0}

        # Today's CO2 saved (kg)
        try:
            cursor.execute("""
                SELECT IFNULL(SUM(carbon_saved), 0) AS co2_saved
                FROM environment_log
                WHERE user_id = %s AND DATE(log_date) = CURDATE()
            """, (session['user_id'],))
            today_env_row = cursor.fetchone() or {"co2_saved": 0}
        except mysql.connector.Error:
            today_env_row = {"co2_saved": 0}

        today_burned = today_burned_row.get('total_burned', 0) or 0
        today_net = (today.get('total_calories', 0) or 0) - today_burned
        today_co2_saved = today_env_row.get('co2_saved', 0) or 0

        # Recent foods
        try:
            cursor.execute("""
                SELECT food_name, quantity, calories, log_date AS created_at
                FROM food_log
                WHERE user_id = %s
                ORDER BY log_date DESC
                LIMIT 10
            """, (session['user_id'],))
            recent_foods = cursor.fetchall() or []
        except mysql.connector.Error:
            cursor.execute("""
                SELECT food_name, quantity, calories
                FROM food_log
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT 10
            """, (session['user_id'],))
            recent_foods = cursor.fetchall() or []
            for item in recent_foods:
                item['created_at'] = ''

        for item in recent_foods:
            date_val = item.get('created_at')
            if date_val and hasattr(date_val, 'strftime'):
                item['created_at_display'] = date_val.strftime('%d %b %Y, %I:%M %p')
            elif date_val:
                item['created_at_display'] = str(date_val)
            else:
                item['created_at_display'] = '--'

        quotes = [
            "Consistency beats intensity. Keep showing up!",
            "Every healthy choice is a vote for the future you want.",
            "You don’t have to be extreme, just consistent.",
            "Strong body, stronger mind—one step at a time.",
            "Fuel your body, focus your mind, follow your plan."
        ]

        weekly_report = []
        weekly_summary = {
            'calories_in': 0,
            'calories_burned': 0,
            'minutes': 0,
            'distance': 0,
            'sessions': 0,
            'average_in': 0,
            'average_burned': 0,
            'calorie_balance': 0,
            'days_logged': 0,
            'days_active': 0
        }

        ai_suggestions = {
            'quote': random.choice(quotes),
            'diet': "Log your meals every day to build a clear picture of your intake.",
            'workout': "Aim for at least 150 minutes of activity spread across the week."
        }

        today_date = datetime.now().date()
        week_dates = [today_date - timedelta(days=delta) for delta in range(6, -1, -1)]
        week_start = week_dates[0]
        week_end = week_dates[-1]

        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        try:
            cursor.execute("""
                SELECT DATE(log_date) AS day, IFNULL(SUM(calories), 0) AS total_calories
                FROM food_log
                WHERE user_id = %s AND DATE(log_date) BETWEEN %s AND %s
                GROUP BY day
            """, (session['user_id'], week_start, week_end))
            food_rows = cursor.fetchall() or []

            cursor.execute("""
                SELECT DATE(log_date) AS day,
                       IFNULL(SUM(calories_burned), 0) AS total_burned,
                       IFNULL(SUM(duration), 0) AS total_duration,
                       COUNT(*) AS sessions
                FROM exercise_log
                WHERE user_id = %s AND DATE(log_date) BETWEEN %s AND %s
                GROUP BY day
            """, (session['user_id'], week_start, week_end))
            exercise_rows = cursor.fetchall() or []

            cursor.execute("""
                SELECT DATE(log_date) AS day,
                       activity,
                       duration,
                       calories_burned
                FROM exercise_log
                WHERE user_id = %s AND DATE(log_date) BETWEEN %s AND %s
                ORDER BY log_date DESC
            """, (session['user_id'], week_start, week_end))
            exercise_detail_rows = cursor.fetchall() or []

            try:
                cursor.execute("""
                    SELECT DATE(log_date) AS day,
                           IFNULL(SUM(distance_walked), 0) AS total_distance
                    FROM environment_log
                    WHERE user_id = %s AND DATE(log_date) BETWEEN %s AND %s
                    GROUP BY day
                """, (session['user_id'], week_start, week_end))
                env_rows = cursor.fetchall() or []
            except mysql.connector.Error:
                env_rows = []

            food_map = {}
            for row in food_rows:
                day = row.get('day')
                if day:
                    key = day.isoformat() if hasattr(day, 'isoformat') else str(day)
                    food_map[key] = safe_float(row.get('total_calories'))

            exercise_map = {}
            for row in exercise_rows:
                day = row.get('day')
                if day:
                    key = day.isoformat() if hasattr(day, 'isoformat') else str(day)
                    exercise_map[key] = {
                        'burned': safe_float(row.get('total_burned')),
                        'duration': safe_float(row.get('total_duration')),
                        'sessions': int(row.get('sessions') or 0)
                    }

            exercise_detail_map = {}
            for row in exercise_detail_rows:
                day = row.get('day')
                if day:
                    key = day.isoformat() if hasattr(day, 'isoformat') else str(day)
                    entry = {
                        'activity': row.get('activity') or 'Session',
                        'duration': int(round(safe_float(row.get('duration')))),
                        'calories_burned': int(round(safe_float(row.get('calories_burned'))))
                    }
                    exercise_detail_map.setdefault(key, []).append(entry)

            env_map = {}
            for row in env_rows:
                day = row.get('day')
                if day:
                    key = day.isoformat() if hasattr(day, 'isoformat') else str(day)
                    env_map[key] = safe_float(row.get('total_distance'))

            totals = {
                'calories_in': 0.0,
                'calories_burned': 0.0,
                'minutes': 0.0,
                'distance': 0.0,
                'sessions': 0
            }

            for day in week_dates:
                key = day.isoformat()
                consumed = round(food_map.get(key, 0.0))
                exercise_data = exercise_map.get(key, {'burned': 0.0, 'duration': 0.0, 'sessions': 0})
                burned = round(exercise_data['burned'])
                duration = int(round(exercise_data['duration']))
                sessions = exercise_data['sessions']
                distance = env_map.get(key, 0.0)

                weekly_report.append({
                    'date_label': day.strftime('%a %d %b'),
                    'calories_in': int(consumed),
                    'calories_out': int(burned),
                    'exercise_minutes': duration,
                    'sessions': sessions,
                    'distance': round(distance, 2),
                    'exercises': exercise_detail_map.get(key, [])
                })

                totals['calories_in'] += consumed
                totals['calories_burned'] += burned
                totals['minutes'] += duration
                totals['distance'] += distance
                totals['sessions'] += sessions

            logged_days = sum(1 for entry in weekly_report if entry['calories_in'] or entry['calories_out'])
            active_days = sum(1 for entry in weekly_report if entry['exercise_minutes'] > 0)

            if weekly_report:
                weekly_summary['calories_in'] = int(round(totals['calories_in']))
                weekly_summary['calories_burned'] = int(round(totals['calories_burned']))
                weekly_summary['minutes'] = int(round(totals['minutes']))
                weekly_summary['distance'] = round(totals['distance'], 2)
                weekly_summary['sessions'] = totals['sessions']
                weekly_summary['average_in'] = int(round(totals['calories_in'] / len(weekly_report)))
                weekly_summary['average_burned'] = int(round(totals['calories_burned'] / len(weekly_report)))
                weekly_summary['calorie_balance'] = weekly_summary['calories_in'] - weekly_summary['calories_burned']
                weekly_summary['days_logged'] = logged_days
                weekly_summary['days_active'] = active_days

        except mysql.connector.Error:
            pass

        tracking_streak = calculate_tracking_streak(weekly_report)
        badges = [
            {
                'title': 'First 1 km walk',
                'earned': weekly_summary.get('distance', 0) >= 1,
                'detail': 'Walk a total of 1 km to unlock',
                'icon': '🚶'
            },
            {
                'title': '7-day tracking streak',
                'earned': tracking_streak >= 7,
                'detail': 'Log meals or workouts every day for a week',
                'icon': '🔥'
            },
            {
                'title': '2000 calories burned',
                'earned': weekly_summary.get('calories_burned', 0) >= 2000,
                'detail': 'Burn 2000 kcal through workouts',
                'icon': '🏅'
            }
        ]

        smart_suggestions = []
        if today_net > 500:
            smart_suggestions.append({
                'title': 'Balance reminder',
                'message': 'You are in a calorie surplus today. Add a light cardio session or swap sugary snacks.',
                'type': 'reminder'
            })
        else:
            smart_suggestions.append({
                'title': 'Great balance',
                'message': 'Your calorie balance looks on track. Keep meals colorful and hydrated.',
                'type': 'positive'
            })

        if tracking_streak < 3:
            smart_suggestions.append({
                'title': 'Build your streak',
                'message': 'Log something tomorrow to push your streak higher and unlock badges.',
                'type': 'tip'
            })
        else:
            smart_suggestions.append({
                'title': 'Streak booster',
                'message': f'You are on a {tracking_streak}-day streak. Schedule tomorrow’s meal log now.',
                'type': 'positive'
            })

        avg_in = weekly_summary.get('average_in', 0)
        balance = weekly_summary.get('calorie_balance', 0)
        total_minutes = weekly_summary.get('minutes', 0)
        active_days = weekly_summary.get('days_active', 0)
        logged_days = weekly_summary.get('days_logged', 0)

        if logged_days == 0:
            diet_tip = "Start logging your meals this week so we can tailor suggestions for you."
        elif avg_in > 2200:
            diet_tip = f"You're averaging {avg_in} kcal per day. Consider lighter meals with lean protein and veggies to balance your intake."
        elif avg_in < 1600:
            diet_tip = f"Your daily intake averages {avg_in} kcal. Make sure you're fueling enough with whole grains, healthy fats, and protein."
        else:
            diet_tip = "Your calorie intake sits in a steady range—keep focusing on whole foods, hydration, and consistency."

        if total_minutes == 0:
            workout_tip = "No workouts recorded yet. Schedule three short sessions this week to get moving."
        elif total_minutes < 150:
            shortfall = 150 - total_minutes
            workout_tip = f"You logged {total_minutes} workout minutes this week. Add {shortfall} more minutes with brisk walks or quick home sessions to hit the 150-minute goal."
        else:
            workout_tip = f"Great job! {total_minutes} workout minutes logged this week. Maintain the streak with mix of strength and mobility."

        if balance > 500 and logged_days > 0:
            diet_tip += " Try dialing back sugary snacks to help close the calorie gap."
        elif balance < -300 and logged_days > 0:
            diet_tip += " You're running a calorie deficit—ensure you're recovering well and getting enough nutrients."

        if active_days < 3 and total_minutes >= 0:
            workout_tip += " Aim to be active on at least 3 days next week to build momentum."

        ai_suggestions['diet'] = diet_tip
        ai_suggestions['workout'] = workout_tip

        cursor.close()
        conn.close()

        return render_template(
            'dashboard.html',
            user_name=user_name,
            user_id=session['user_id'],
            today_total_calories=today.get('total_calories', 0),
            today_food_count=today.get('items', 0),
            today_burned=today_burned,
            today_net=today_net,
            today_co2_saved=today_co2_saved,
            recent_foods=recent_foods,
            weekly_report=weekly_report,
            weekly_summary=weekly_summary,
            ai_suggestions=ai_suggestions,
            badges=badges,
            tracking_streak=tracking_streak,
            smart_suggestions=smart_suggestions
        )
    else:
        return redirect(url_for('login'))


# ------------------ ADD FOOD LOG ------------------
@app.route('/add_food', methods=['POST'])
def add_food():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    food_name = request.form['food_name'].strip()
    quantity_raw = request.form.get('quantity', '1').strip()
    
    try:
        quantity = max(int(quantity_raw), 1)
    except ValueError:
        quantity = 1
    
    # Auto-calculate calories from fruit name
    calories_per_unit = get_fruit_calories(food_name)
    calories = calories_per_unit * quantity if calories_per_unit is not None else None
    
    # If not a known fruit, try to get manual input (fallback)
    if calories is None:
        calories_input = request.form.get('calories', '').strip()
        if calories_input:
            try:
                calories = float(calories_input)
            except ValueError:
                calories = 0
        else:
            # Default if no fruit match and no manual input
            calories = 0

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO food_log (user_id, food_name, quantity, calories) VALUES (%s, %s, %s, %s)",
            (session['user_id'], food_name, quantity, calories)
        )
        conn.commit()
    except mysql.connector.Error as e:
        # Handle the case where a database trigger references a non-existent user_summary table
        error_msg = str(e).lower()
        if "user_summary" in error_msg and "doesn't exist" in error_msg:
            # Rollback and try to disable/ignore trigger errors
            try:
                conn.rollback()
                # Try inserting again - if trigger fails, the insert might still work
                # This is a workaround for triggers that reference missing tables
                cursor.execute(
                    "INSERT INTO food_log (user_id, food_name, quantity, calories) VALUES (%s, %s, %s, %s)",
                    (session['user_id'], food_name, quantity, calories)
                )
                try:
                    conn.commit()
                except mysql.connector.Error:
                    # If commit fails due to trigger, the data might still be inserted
                    # Try a simple commit without checking for trigger errors
                    conn.commit()
            except mysql.connector.Error:
                # If all else fails, just rollback and show error
                conn.rollback()
                cursor.close()
                conn.close()
                return f"Error adding food log. Please check database triggers. Original error: {str(e)}"
        else:
            # For other errors, raise normally
            conn.rollback()
            cursor.close()
            conn.close()
            raise
    
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard'))


# ------------------ ADD EXERCISE LOG ------------------
@app.route('/add_exercise', methods=['POST'])
def add_exercise():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    activity = request.form.get('activity', '').strip()
    duration = request.form.get('duration', '0').strip()

    try:
        duration_min = int(duration)
    except ValueError:
        duration_min = 0

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user's profile data (weight, height, age) for accurate calorie calculation
    cursor.execute("SELECT weight, height, age FROM users WHERE id = %s", (session['user_id'],))
    user_data = cursor.fetchone()
    
    weight_kg = user_data.get('weight') if user_data and user_data.get('weight') else 70.0  # Default 70kg
    height_cm = user_data.get('height') if user_data and user_data.get('height') else 170.0  # Default 170cm
    age = user_data.get('age') if user_data and user_data.get('age') else 30  # Default 30 years
    
    # Auto-calculate calories burned using MET formula based on user's stats
    calories_burned_val = calculate_calories_burned(
        activity=activity,
        duration_minutes=duration_min,
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age
    )
    
    cursor.execute(
        "INSERT INTO exercise_log (user_id, activity, duration, calories_burned) VALUES (%s, %s, %s, %s)",
        (session['user_id'], activity, duration_min, calories_burned_val)
    )
    conn.commit()

    # Environment impact for walking only (distance + CO2 saved)
    # Assume 5 km/h => 0.0833 km/min; CO2 saved ≈ 0.21 kg per km not driven
    if activity.lower() == 'walking':
        distance_km = duration_min * (5.0 / 60.0)
        carbon_saved_kg = distance_km * 0.21
        try:
            cursor.execute(
                "INSERT INTO environment_log (user_id, distance_walked, carbon_saved) VALUES (%s, %s, %s)",
                (session['user_id'], distance_km, carbon_saved_kg)
            )
            conn.commit()
        except mysql.connector.Error:
            pass

    cursor.close()
    conn.close()

    return redirect(url_for('dashboard'))




# ------------------ API (For Mobile App - Later) ------------------
@app.route('/api/summary/<int:user_id>')
def summary_api(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            IFNULL(SUM(calories), 0) AS total_calories_consumed
        FROM food_log
        WHERE user_id = %s
    """, (user_id,))

    summary = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify(summary)


# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ------------------ ENTRIES (All DB rows) ------------------
@app.route('/entries')
def entries():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM users ORDER BY id DESC")
    users = cursor.fetchall() or []
    try:
        cursor.execute("""
            SELECT id, user_id, food_name, quantity, calories, log_date AS created_at
            FROM food_log
            ORDER BY id DESC
            LIMIT 200
        """)
        foods = cursor.fetchall() or []
    except mysql.connector.Error:
        foods = []
    cursor.close()
    conn.close()

    return render_template('entries.html', users=users, foods=foods)


# ------------------ RUN SERVER ------------------
if __name__ == '__main__':
    app.run(debug=True)
