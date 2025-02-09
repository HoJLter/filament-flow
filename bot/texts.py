from aiogram.fsm.context import FSMContext

text_welcome = ("Здравствуй! Это бот для оформления заказов на 3D печать."
                "\nДля ознакомления можешь зайти в раздел информации")

text_info = ("✍️ Для оформления заказа заполните параметры в меню \"оформить заказ\" \n"
        "📭 В качестве службы доставки мы используем Почту России.\n"
        "⏳ Время доставки уточняйте у менеджера")

text_order_edit_complete = "Оформление завершено ✅ Скоро с вами свяжется администратор для уточнения деталей"

async def text_order_menu_gen(state: FSMContext):
    data = (await state.get_data())['order_parameters']
    text =(
          f"\nНазвание заказа: {data.get("order_name") or " Введите имя заказа"}"
          f"\nТехническое задание: {data.get("references") or " Введите ТЗ"}"
          f"\nПочтовый индекс:{data.get("mail_index") or " Введите почтовый индекс"}"
          f"\nФайл: {data.get("file_name") or  "Отправьте .stl файл"}"
          )
    return text


index_error_text = ("Такой индекс не был найден в нашей базе данных."
                    " Вы уверены, что указали почтовый индекс правильно?"
                    " Если да, то можете обратиться к нашему менеджеру")


image_welcome = 'AgACAgIAAxkBAAMlZ6d-h1N3fvQFev8E-TQtkyP34koAAv_nMRsMpDlJUhOUiCC7cOcBAAMCAAN5AAM2BA'
image_info = 'AgACAgIAAxkBAAMnZ6d-9vFn8AruU4cTC4dZ3aD9eVwAAgroMRsMpDlJ1wvosAABucJEAQADAgADeQADNgQ'
image_order_menu = 'AgACAgIAAxkBAAMmZ6d-pD6v-4seOx0i91ej2ED5TTYAAgXoMRsMpDlJ0GdURj5mXGkBAAMCAAN5AAM2BA'
image_order_name = 'AgACAgIAAxkBAAMqZ6d_P8LsZghRiD8pc922NSRjoOkAAg3oMRsMpDlJWemhOsetYPsBAAMCAAN5AAM2BA'
image_reference = 'AgACAgIAAxkBAAMrZ6d_U1RD2L3_Rm5ytn6sb_OyFtUAAg7oMRsMpDlJxRGx-BbJwfMBAAMCAAN5AAM2BA'
image_mail_indexes = 'AgACAgIAAxkBAAPkZ6hn7uensVsF9J4ZoNjRfc2B8tIAAoTlMRsMpEFJsvmlZWnVahUBAAMCAAN5AAM2BA'
image_file = 'AgACAgIAAxkBAAMtZ6d_dxWtd6PB1ANuhHtghnzQVXUAAhHoMRsMpDlJF0gkwUfvaOIBAAMCAAN5AAM2BA'
image_admin_panel = "AgACAgIAAxkBAAMuZ6d_g4UvP7ox-nVgweLCw67Q75EAAhLoMRsMpDlJ7L5rcxWTxAABAQADAgADeQADNgQ"
