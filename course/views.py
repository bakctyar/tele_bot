from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async

from payment.views import payment
from .models import Course
from buyers.models import OrderCourse, SignedPeople

keyboard_purchases_course = [
    [InlineKeyboardButton('Купить', callback_data='buy')],
    [InlineKeyboardButton('вернуться назад', callback_data='go_back')]
]

async def list_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data in ['agree', 'go_back']:
        try:
            # Получаем все курсы из базы данных
            base_courses = Course.objects.all()
            courses = await sync_to_async(list)(base_courses)

            keyboard = []
            if courses:
                # Создаем строки кнопок
                for course in courses:
                    button = InlineKeyboardButton(course.title, callback_data=f"course_{course.id}")

                    keyboard.append([button])  # Оборачиваем каждую кнопку в список для создания новой строки

                # Форматируем разметку для кнопок
                reply_markup = InlineKeyboardMarkup(keyboard)
                message_text = "Нажмите на выбранный курс и получите об этом курсе более подроюную информацию:"
            else:
                message_text = "Нет доступных курсов."
                reply_markup = None  # Нет кнопок, только текст

            # Обновляем сообщение
            await query.edit_message_text(message_text, reply_markup=reply_markup)

        except Exception as e:
            # Ловим исключения и отображаем сообщение об ошибке
            await query.edit_message_text("Ошибка при получении курсов. Попробуйте позже.")




async def choice_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    reply_markup = InlineKeyboardMarkup(keyboard_purchases_course)


    course_id = query.data.split("_")[-1]
    if course_id:
        try:
            course = await sync_to_async(Course.objects.get)(id=int(course_id))
            await query.edit_message_text(
                f'<b>{course.title}</b>\n\n{course.description}',
                parse_mode='HTML', reply_markup=reply_markup
            )
            context.user_data['selection_data'] = course

        except Course.DoesNotExist:
            await query.edit_message_text(text=f'нет такого курса')
    else:
        await query.edit_message_text(text='Некорректный запрос.')


async def buy_or_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "buy":
        await payment(update, context)
    if query.data == "go_back":
        await list_course(update, context)


async def my_course_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        user = await sync_to_async(SignedPeople.objects.get)(user_id=user_id)
        order_courses = await sync_to_async(lambda: list(OrderCourse.objects.select_related('course').filter(user=user)))()
        course_titles = [order_course.course.title for order_course in order_courses]

        # Формируем сообщение
        if course_titles:
            response_message = "Мои курсы:\n" + '\n'.join(course_titles)
        else:
            response_message = "Мои курсы:\nУ вас нет курсов."
        await update.message.reply_text(text=response_message)

    except SignedPeople.DoesNotExist:
        await update.message.reply_text('Не удалось найти ваши курсы. Попробуйте позже.')
    except Exception as e:
        await update.message.reply_text('Не удалось получить ваши курсы. Попробуйте позже.')






