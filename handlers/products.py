@router.callback_query(F.data.startswith("edit_product_"))
async def edit_product_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    if not user:
        await callback.answer()
        return
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user.id
    ).first()
    
    if not product:
        if user.language == 'ru':
            text = "❌ Товар не найден"
        else:
            text = "❌ Product not found"
        
        await callback.message.answer(text)
        await callback.answer()
        return
    
    if user.language == 'ru':
        text = f"""✏️ Редактирование товара: {product.name}

Выберите что изменить:
1. Название
2. Количество
3. Закупочную цену
4. Цену продажи
5. Категорию

Введите номер поля для редактирования:"""
    else:
        text = f"""✏️ Editing product: {product.name}

Choose what to edit:
1. Name
2. Quantity
3. Purchase price
4. Sale price
5. Category

Enter field number to edit:"""
    
    await callback.message.answer(
        text,
        reply_markup=get_cancel_keyboard(user.language)
    )
    await state.set_state(ProductStates.editing_product)
    await state.update_data(language=user.language, product_id=product_id)
    await callback.answer()

@router.message(ProductStates.editing_product)
async def process_edit_field(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    
    if message.text == ("❌ Отмена" if language == 'ru' else "❌ Cancel"):
        await state.clear()
        await message.answer(
            "🚫 Редактирование отменено" if language == 'ru' else "🚫 Editing cancelled",
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    field_map = {
        '1': 'name',
        '2': 'quantity',
        '3': 'purchase_price',
        '4': 'sale_price',
        '5': 'category'
    }
    
    choice = message.text.strip()
    if choice not in field_map:
        if language == 'ru':
            error_text = "❌ Пожалуйста, выберите номер от 1 до 5:"
        else:
            error_text = "❌ Please choose a number from 1 to 5:"
        
        await message.answer(error_text)
        return
    
    field = field_map[choice]
    await state.update_data(editing_field=field)
    
    field_prompts = {
        'ru': {
            'name': "Введите новое название товара:",
            'quantity': "Введите новое количество:",
            'purchase_price': "Введите новую закупочную цену:",
            'sale_price': "Введите новую цену продажи:",
            'category': "Выберите новую категорию:"
        },
        'en': {
            'name': "Enter new product name:",
            'quantity': "Enter new quantity:",
            'purchase_price': "Enter new purchase price:",
            'sale_price': "Enter new sale price:",
            'category': "Choose new category:"
        }
    }
    
    prompt = field_prompts.get(language, field_prompts['ru'])[field]
    
    if field == 'category':
        # Show categories keyboard
        db: Session = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        categories = db.query(Category).filter(Category.user_id == user.id).all()
        
        if categories:
            await message.answer(
                prompt,
                reply_markup=get_categories_keyboard(categories, language)
            )
        else:
            if language == 'ru':
                text = "📁 У вас нет категорий. Создайте сначала категорию."
            else:
                text = "📁 You have no categories. Create a category first."
            
            await message.answer(text)
            await state.clear()
    else:
        await message.answer(prompt)
    
    await state.set_state(ProductStates.editing_field)

@router.message(ProductStates.editing_field)
async def process_field_value(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')
    product_id = data.get('product_id')
    field = data.get('editing_field')
    
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user.id
    ).first()
    
    if not product:
        await state.clear()
        return
    
    value = message.text.strip()
    
    try:
        if field == 'name':
            if len(value) < 2:
                raise ValueError("Name too short")
            product.name = value
            
        elif field == 'quantity':
            if not is_valid_quantity(value):
                raise ValueError("Invalid quantity")
            product.quantity = int(value)
            
        elif field == 'purchase_price':
            if not is_valid_price(value):
                raise ValueError("Invalid price")
            purchase_price = float(value)
            product.purchase_price = purchase_price
            # Recalculate profit
            product.profit = product.sale_price - purchase_price
            
        elif field == 'sale_price':
            if not is_valid_price(value):
                raise ValueError("Invalid price")
            sale_price = float(value)
            product.sale_price = sale_price
            # Recalculate profit
            product.profit = sale_price - product.purchase_price
            
        product.updated_at = datetime.utcnow()
        db.commit()
        
        if language == 'ru':
            success_text = f"✅ Товар '{product.name}' успешно обновлен!"
        else:
            success_text = f"✅ Product '{product.name}' successfully updated!"
        
        await message.answer(
            success_text,
            reply_markup=get_main_menu_keyboard(language)
        )
        
    except ValueError as e:
        if language == 'ru':
            error_text = f"❌ Ошибка: {str(e)}. Попробуйте снова:"
        else:
            error_text = f"❌ Error: {str(e)}. Try again:"
        
        await message.answer(error_text)
        return
    
    await state.clear()

@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    if not user:
        await callback.answer()
        return
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user.id
    ).first()
    
    if not product:
        if user.language == 'ru':
            text = "❌ Товар не найден"
        else:
            text = "❌ Product not found"
        
        await callback.message.answer(text)
        await callback.answer()
        return
    
    if user.language == 'ru':
        text = f"⚠️ Вы уверены, что хотите удалить товар '{product.name}'?"
    else:
        text = f"⚠️ Are you sure you want to delete product '{product.name}'?"
    
    await callback.message.answer(
        text,
        reply_markup=get_yes_no_keyboard(user.language)
    )
    
    # Store product_id in callback data for confirmation
    await callback.answer()

@router.callback_query(F.data == "confirm_yes")
async def confirm_product_delete(callback: CallbackQuery):
    # In a real implementation, you would need to track which product is being deleted
    # This is a simplified version
    await callback.answer("⚠️ Функция удаления требует дополнительной реализации")
