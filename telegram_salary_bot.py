import telebot
from telebot import types

# Ваш токен
TOKEN = '7172377394:AAFf76xcYwj2iKPFF5bB1UXbUsMquUP1Cb4'
bot = telebot.TeleBot(TOKEN)

# Хранение данных пользователя
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Начать расчет зарплаты"))
    bot.send_message(message.chat.id, "Привет! Я бот для расчета заработной платы тренера. Нажмите кнопку ниже, чтобы начать!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Начать расчет зарплаты")
def start_salary_calculation(message):
    ask_month(message)

def ask_month(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    for month in months:
        markup.add(month)
    msg = bot.send_message(message.chat.id, "Выберите месяц:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_month)

def process_month(message):
    user_data[message.chat.id]['month'] = message.text
    msg = bot.send_message(message.chat.id, "Введите сумму продаж (тенге):")
    bot.register_next_step_handler(msg, process_sales)

def process_sales(message):
    try:
        sales = float(message.text.replace(' ', ''))
        user_data[message.chat.id]['sales'] = sales
        msg = bot.send_message(message.chat.id, "Введите сумму продаж секций (тенге):")
        bot.register_next_step_handler(msg, process_section_sales)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректное число для суммы продаж:")
        bot.register_next_step_handler(msg, process_sales)

def process_section_sales(message):
    try:
        section_sales = float(message.text.replace(' ', ''))
        user_data[message.chat.id]['section_sales'] = section_sales
        msg = bot.send_message(message.chat.id, "Введите количество проведенных тренировок:")
        bot.register_next_step_handler(msg, process_sessions)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректное число для суммы продаж секций:")
        bot.register_next_step_handler(msg, process_section_sales)

def process_sessions(message):
    try:
        sessions = int(message.text)
        user_data[message.chat.id]['sessions'] = sessions
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        categories = ["Тренер", "Мастер тренер", "Эксперт тренер", "Эксперт плюс", "Премиум тренер"]
        for category in categories:
            markup.add(category)
        msg = bot.send_message(message.chat.id, "Выберите категорию тренера:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_category)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректное число для количества тренировок:")
        bot.register_next_step_handler(msg, process_sessions)

def process_category(message):
    user_data[message.chat.id]['category'] = message.text
    msg = bot.send_message(message.chat.id, "Введите количество дней отпуска:")
    bot.register_next_step_handler(msg, process_vacation)

def process_vacation(message):
    try:
        vacation_days = int(message.text)
        user_data[message.chat.id]['vacation_days'] = vacation_days
        msg = bot.send_message(message.chat.id, "Введите сумму реализации (тенге):")
        bot.register_next_step_handler(msg, process_realization)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректное число для количества дней отпуска:")
        bot.register_next_step_handler(msg, process_vacation)

def process_realization(message):
    try:
        realization = float(message.text.replace(' ', ''))
        user_data[message.chat.id]['realization'] = realization
        msg = bot.send_message(message.chat.id, "Введите дополнительный бонус (%):")
        bot.register_next_step_handler(msg, process_bonus)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректное число для суммы реализации:")
        bot.register_next_step_handler(msg, process_realization)

def process_bonus(message):
    try:
        bonus = float(message.text)
        user_data[message.chat.id]['bonus'] = bonus
        msg = bot.send_message(message.chat.id, "Введите квартальный бонус (%):")
        bot.register_next_step_handler(msg, process_quarter_bonus)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректное число для дополнительного бонуса:")
        bot.register_next_step_handler(msg, process_bonus)

def process_quarter_bonus(message):
    try:
        quarter_bonus = float(message.text)
        user_data[message.chat.id]['quarter_bonus'] = quarter_bonus
        calculate_salary(message)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректное число для квартального бонуса:")
        bot.register_next_step_handler(msg, process_quarter_bonus)

def calculate_salary(message):
    data = user_data[message.chat.id]
    base_rate = {
        'Тренер': 73000,
        'Мастер тренер': 92000,
        'Эксперт тренер': 112000,
        'Эксперт плюс': 135000,
        'Премиум тренер': 165000
    }.get(data['category'], 0)

    # Уменьшение плана с учетом отпускных дней
    month_days = 30  # Упрощение для расчета
    plan = base_rate * 12 * ((month_days - data['vacation_days']) / month_days)

    # Расчет процентов за количество тренировок
    sessions = data['sessions']
    if sessions < 60:
        percentage = 0.40
    elif sessions < 80:
        percentage = 0.46
    elif sessions < 100:
        percentage = 0.48
    elif sessions <= 120:
        percentage = 0.50
    else:
        percentage = 0.52

    # Расчет бонуса за продажи
    sales = data['sales']
    if sales < 0.56 * plan:
        sales_bonus_percentage = -0.02
    elif sales <= 1.1 * plan:
        sales_bonus_percentage = 0
    elif sales <= 1.3 * plan:
        sales_bonus_percentage = 0.02
    elif sales <= 1.8 * plan:
        sales_bonus_percentage = 0.04
    else:
        sales_bonus_percentage = 0.08

    # Итоговый процент
    bonus_percentage = data['bonus'] / 100
    quarter_bonus_percentage = data['quarter_bonus'] / 100
    final_percentage = percentage + sales_bonus_percentage + bonus_percentage + quarter_bonus_percentage

    # Расчет заработной платы
    realization = data['realization']
    session_earnings = realization * final_percentage
    section_sales = data['section_sales']
    section_earnings = section_sales * 0.45
    quarter_bonus = (realization * quarter_bonus_percentage)
    additional_bonus = (realization * bonus_percentage)
    total_salary = session_earnings + section_earnings + additional_bonus + quarter_bonus

    # Отправка пользователю всех расчетов
    result_message = (
        f"План: {plan:,.2f} тенге\n"
        f"Процент за количество тренировок: {(percentage * 100):.2f}%\n"
        f"Процент за продажи: {(sales_bonus_percentage * 100):.2f}%\n"
        f"Дополнительный бонус: {data['bonus']}%\n"
        f"Квартальный бонус: {data['quarter_bonus']}%\n"
        f"Итоговый процент: {(final_percentage * 100):.2f}%\n"
        f"Заработная плата с персональных тренировок: {session_earnings:,.2f} тенге\n"
        f"Заработная плата с секций (45%): {section_earnings:,.2f} тенге\n"
        f"Дополнительный бонус: {additional_bonus:,.2f} тенге\n"
        f"Квартальный бонус: {quarter_bonus:,.2f} тенге\n"
        f"Итоговая зарплата: {total_salary:,.2f} тенге"
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Начать заново"))
    bot.send_message(message.chat.id, result_message, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Начать заново")
def restart(message):
    start(message)

if __name__ == '__main__':
    bot.polling(none_stop=True)