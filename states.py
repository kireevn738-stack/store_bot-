from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_language = State()
    waiting_for_store_name = State()


class ProductStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_purchase_price = State()
    waiting_for_sale_price = State()
    waiting_for_quantity = State()
    waiting_for_sku = State()
    waiting_for_description = State()
    
    editing_product = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()


class CategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    
    editing_category = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()


class AnalyticsStates(StatesGroup):
    waiting_for_period_type = State()
    waiting_for_custom_start = State()
    waiting_for_custom_end = State()
